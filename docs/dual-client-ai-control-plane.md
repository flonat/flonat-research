# Building a Client-Neutral AI Control Plane

> A shareable architectural recap of a working Claude Code–Codex and
> cross-machine integration. This document explains the design and adoption
> process without requiring access to the reference installation.

## Executive summary

The goal was not to make Claude Code and Codex look identical. They have
different configuration formats, hook events, native tools, MCP support, and
runtime state. The goal was to give both clients access to the same reviewed
working system without maintaining two drifting implementations.

The resulting model has four layers:

```text
client-neutral, versioned sources
              │
              ▼
capability contracts + deterministic renderers
              │
       ┌──────┴──────┐
       ▼             ▼
Claude adapters   Codex adapters
       │             │
       └──────┬──────┘
              ▼
machine-local deployment + receipts + doctor
```

Git transports the control plane between machines. Each machine then deploys
its own copies into the two client homes. Files carry durable context between
clients; client histories, authentication, caches, and internal databases stay
local. Unsupported capabilities are explicit rather than silently omitted.

The central principle is:

> Share intent and durable state through neutral, versioned files; adapt at the
> client boundary; deploy independently on every machine.

## What problem this solves

A naive dual-client setup usually accumulates several independent sources of
truth:

- a skill edited under one client's home directory;
- a different version copied into the other client's directory;
- machine-specific absolute paths embedded in instructions;
- MCP registrations changed manually on one host;
- hooks that imply context has been saved when only one client can see it;
- a second machine that appears current because Git is current while deployed
  files or external data are stale.

Blind bidirectional filesystem sync does not solve these problems. It mixes
portable source with runtime-owned files and cannot make sensible decisions
when two copies diverge. The control-plane model replaces that ambiguity with
declared ownership, reviewable transformations, and observable deployment
state.

## The synchronization modalities

There are three distinct synchronization problems. Treating them separately is
essential.

### 1. Claude Code and Codex on the same machine

Claude Code and Codex do not copy configuration to each other. They consume
adapters rendered from the same canonical assets:

| Asset | Canonical form | Claude Code | Codex |
|---|---|---|---|
| Skills | neutral skill body plus capability contract | native body or thin command adapter | compatible body in the Codex-discovered skill root |
| Agents | neutral agent contract | generated Markdown adapter | generated TOML adapter |
| Rules | canonical semantic rule | native rule or global guidance | selected lean guidance or supported policy adapter |
| Hooks | invariant plus event mapping | richer lifecycle events | supported hook events, file fallback, or explicit unavailability |
| MCP/CLI access | surface matrix and package ownership | MCP or CLI as declared | MCP where appropriate, otherwise CLI fallback |
| Context | project and control-plane files | hook-assisted read/write | the same files, with hooks optional |

The deployment engine hashes both source and destination content. A normal
deployment is allowed only from committed source that matches its upstream.
This prevents an unreviewed local experiment from becoming an apparently
verified installation.

### 2. The same control plane on multiple machines

Git is the transport for canonical infrastructure:

```text
Machine A: edit → validate → commit → push
                                      │
                                      ▼
Machine B: pull --ff-only → deploy locally → doctor
```

Client home directories are never copied between machines. Each machine owns
its absolute paths, authentication, runtime databases, caches, and deployment
receipt. Machine-local overrides are narrow, untracked overlays rather than
forks of canonical files.

Fast-forward pulls are safe to automate. Divergent history or dirty files that
overlap incoming changes stop before deployment. Unrelated routine state does
not needlessly block a pull. An always-on machine can poll and converge
silently, while a laptop can remain manual and offline-tolerant.

### 3. Work continuity between sessions and clients

Durable context is files-first:

- project guidance explains stable conventions;
- `.context/ai-handoff.md` records an explicit continuation state;
- `.context/current-focus.md` records active priorities;
- portable memory files hold curated context;
- plans and logs preserve decisions and evidence.

The same handoff protocol supports Claude→Claude, Codex→Codex, Claude→Codex,
and Codex→Claude. It records the source and target client, machine, branch,
commit, worktree ownership, outcome, acceptance criteria, and status. Hooks may
load or update these files as a convenience, but hook execution is never the
only place where shared context exists.

Client transcripts, native session histories, authentication state, and
per-client memory databases are deliberately not synchronized.

## The canonical contract

Every managed surface needs an explicit row in a versioned contract. A useful
schema records:

- stable identifier and asset type;
- canonical source and owning repository;
- supported clients, with no implicit `both` default;
- required semantic capabilities;
- packaging per client: `native`, `adapted`, `fallback`, or `unavailable`;
- dependencies and their transitive availability;
- portability blockers and reviewed exceptions;
- renderer and verification command;
- distribution audience independently of client support.

Capability names should describe behavior, not vendor APIs. For example,
“fresh-context delegation” is the requirement; a Claude sub-agent tool and a
Codex collaboration agent are possible adapters. “Scholarly search” is the
requirement; an MCP call and a subprocess CLI are possible adapters.

This model prevents two common mistakes:

1. claiming parity because the same file was copied even though it cannot run;
2. excluding a workflow merely because its original client-specific syntax is
   not portable.

## Neutral authoring rules

Canonical content should be boringly portable:

- use relative paths for bundled references;
- resolve project roots from a stable indirection file or environment contract;
- avoid absolute user, volume, and cloud-storage paths;
- describe skills by neutral name instead of embedding client slash syntax;
- invoke Python through the project's environment manager;
- never require an MCP-only tool without a declared fallback;
- keep client-specific instructions in explicit adapter blocks;
- keep durable state in files, not a hook cache or task history.

A linter should reject machine-absolute paths, client-home assumptions,
unqualified native tool names, and undeclared MCP dependencies in assets marked
for both clients.

## MCP registrations, CLIs, and credentials

Registrations and credentials are different control planes:

- a matrix declares which capability is registered on which client or host;
- one targeted reconciler merges only the registrations it owns;
- a separate credential workflow materializes local secret files;
- secrets never enter the canonical repository or deployment receipt;
- a CLI fallback exposes shared functionality without requiring identical MCP
  support or loading every tool schema into every query.

Scoped service-account credentials can be provisioned independently on each
machine. The important properties are least privilege, local file permissions,
rotation, and a wrapper that prevents tokens from appearing in commands or
tracked configuration. The transport should synchronize registrations and
policy, not secret material.

## Hooks: functional parity, not event parity

Claude Code may expose more lifecycle events than Codex. Trying to simulate
every event usually creates fragile or expensive startup behavior. Instead,
classify every hook by the invariant it protects:

- safety invariants need a supported enforcement point or must fail closed;
- context conveniences fall back to files and explicit commands;
- unsupported lifecycle conveniences are documented as unavailable;
- session-start checks stay read-only, bounded, and offline-tolerant;
- expensive reconstruction and network checks belong in an explicit doctor.

This approach makes hooks optional adapters around a shared file contract,
rather than prerequisites for continuity.

## Deployment and recovery workflow

The normal operator loop is:

```text
inspect drift
  → import unexpected deployed edits
  → reconcile into the declared canonical owner
  → render adapters
  → validate staged sources
  → commit and push
  → deploy locally
  → run the doctor
```

Direct edits under a client home are not discarded. An import command preserves
the complete divergent bytes, original path, hashes, timestamp, canonical
owner, and resolution evidence. The operator then reconciles the useful change
into canonical source. Force replacement is reserved for reviewed migrations
and creates a backup.

For rapid local testing, use an explicit canary mode. Mark its receipt as
temporary and make the normal doctor fail until a committed, upstream-matching
deployment replaces it. Never silently reinterpret an ordinary deployment as
a local test.

## A unified doctor

A Git SHA alone cannot prove that the working system is current. A useful
doctor reports independent domains with `PASS`, `FAIL`, and
`SKIPPED (not this host)`:

- canonical Git revision and remote-verification age;
- deployed revision and content drift;
- runtime skill, agent, rule, and hook availability;
- MCP registration and CLI-wrapper parity;
- generated downstream receipts;
- credential accessibility without revealing credential values;
- context and memory health;
- machine-specific services and storage;
- external data-plane freshness where the workflows depend on it.

A peer mode should retrieve the other machine's read-only receipt and compare
canonical SHA, deployed SHA, remote SHA, capability-contract digest, runtime
inventory digest, and generated-surface receipts in one table. Peer
unavailability must be reported without erasing local evidence.

Network verification should be opportunistic: after pushes and pulls, during
explicit doctor runs, and as a short asynchronous startup probe. Offline work
remains possible, but stale or unverified evidence is visible.

## Distribution boundaries

Client availability and disclosure audience are separate dimensions. A skill
can work in both clients and still be private. If the system generates friends
or public repositories, each downstream product needs:

- an explicit inclusion and transformation contract;
- deny-by-default handling of unclassified files;
- path, identity, affiliation, secret, and operational-metadata leak guards;
- source and target content receipts;
- a reviewable transition document;
- no access to private handoffs, logs, credentials, machine inventory, or
  health evidence.

The private neutral schema remains canonical. Downstream repositories consume
reviewed projections; they do not become competing authoring sources.

## How to build a similar system

### Stage 1: Inventory before unification

List every skill, agent, rule, hook, registration, CLI, context file, generated
surface, client discovery root, and machine-local dependency. Record where it
is authored, where it is deployed, who owns it, and whether it currently works
on each client.

Do not begin by copying files. The inventory reveals duplicate discovery roots,
generated files mistaken for sources, and workflows that depend on invisible
runtime state.

### Stage 2: Establish canonical ownership

Choose one private, versioned control plane. Move authoring sources there and
treat client homes as generated deployment targets. Add stable path resolution
and narrowly scoped machine-local overlays.

### Stage 3: Introduce capability contracts

Classify assets explicitly. Start with a small vertical slice containing one
skill, one agent, one rule, one safety hook, one convenience hook, and one
external capability. Prove the whole render–deploy–verify loop before bulk
migration.

### Stage 4: Make durable context client-neutral

Create project guidance, handoff, focus, plan, and portable-memory contracts.
Use loss-preserving conflict semantics: select the active variant by a simple
documented rule and retain the displaced full bytes for human reconciliation.

### Stage 5: Render and deploy deterministically

Generate client-native adapters from neutral sources. Hash the source and
target, record the deployed revision, remove retired managed files, preserve
unmanaged runtime state, and make repeated deployments no-ops.

### Stage 6: Separate integrations from secrets

Create one registration matrix, one targeted reconciler, shared CLI wrappers,
and an independent least-privilege credential workflow. Test every declared
fallback from the client that will use it.

### Stage 7: Add transport and observability

Use fast-forward-only Git transport between machines. Add offline-tolerant
remote evidence, a generated-surface registry, a unified doctor, and a peer
receipt comparison. Automate only provably safe convergence paths.

### Stage 8: Migrate in waves and retire old paths

Migrate blocker clusters rather than rewriting everything at once. For each
wave, test runtime discovery, duplicate names, policy preservation, startup
latency, bootstrap reconstruction, and cross-machine parity. Retire old scripts,
aliases, and documentation only after all callers have moved.

## Minimum viable version

A smaller team can adopt the model without reproducing every component. The
minimum useful implementation is:

1. one private canonical repository;
2. one explicit client-availability manifest;
3. deterministic renderers for the formats that differ;
4. a deploy command that records hashes and refuses uncommitted source;
5. a files-first handoff document;
6. fast-forward-only Git transport between machines;
7. a doctor that compares canonical, deployed, and remote revisions;
8. a rule that secrets and runtime-owned client files never synchronize.

MCP reconciliation, memory exchange, automatic convergence, downstream
distribution, and data-plane health can be added after this core is stable.

## What was implemented in this installation

The completed rollout covered:

- a unified contract across skills, agents, rules, hooks, MCP registrations,
  CLIs, and owned support files;
- neutral agent sources with deterministic Claude Markdown and Codex TOML
  adapters;
- explicit skill targeting and single-owner discovery, eliminating duplicate
  skill entries;
- semantic rule coverage and invariant-based hook mappings;
- files-first context, portable memory, and one four-route handoff protocol;
- content-addressed deployment with import, backup, receipt, and local-canary
  semantics;
- fast-forward-only multi-repository transport and safe always-on-machine
  convergence;
- registration/credential separation with CLI fallbacks and scoped secret
  access;
- one host-aware doctor with peer parity and generated-surface receipts;
- guarded private→friends→public projections with aggregate leak checks;
- fresh-home reconstruction tests and retirement of legacy sync mechanisms.

Final acceptance included a complete repository test suite, an isolated
fresh-home bootstrap, repeated zero-change deployments on both machines,
aggregate downstream leak checks, and a peer doctor showing identical
canonical, deployed, remote, availability, runtime, and generated-surface
evidence.

## Lessons and trade-offs

1. **Bidirectional does not mean filesystem mirroring.** Either client can edit
   canonical source, but Git and review arbitrate convergence.
2. **Functional parity is more honest than identical packaging.** Explicit
   fallbacks are better than copied instructions that cannot execute.
3. **Files are the interoperability layer.** Hooks improve ergonomics; they do
   not own shared memory.
4. **One owner per asset prevents UI and policy ambiguity.** Duplicate
   discovery roots are a deployment bug, not harmless redundancy.
5. **Health must include the data plane.** Current configuration is not useful
   when the storage, index, or service behind it is stale.
6. **Offline tolerance and fail-closed behavior are compatible.** Preserve last
   verified evidence, distinguish stale from unverified, and refuse only unsafe
   mutations.
7. **The always-on machine and the laptop need different automation.** The same
   canonical contract can support a poller on one and manual convergence on the
   other.
8. **Downstream sharing is a product boundary.** Public documentation and
   manifests should be generated through reviewed filters, not copied from the
   private control plane.

## Adoption checklist

- [ ] Every managed asset has one canonical owner.
- [ ] Every client target is explicit; there is no silent `both` default.
- [ ] Client-neutral content contains no unmarked machine or client-home paths.
- [ ] Every unavailable capability has a reason and closest safe alternative.
- [ ] Each client discovers a shared asset exactly once.
- [ ] Durable context survives with all client hooks disabled.
- [ ] Registrations and credentials have separate writers.
- [ ] Secrets, transcripts, histories, caches, and runtime databases stay local.
- [ ] Normal deployment requires committed, upstream-matching source.
- [ ] Direct deployment edits can be imported without data loss.
- [ ] Cross-machine transport is fast-forward-only and never auto-resolves.
- [ ] Repeated deployment is a verified no-op.
- [ ] A peer check proves canonical and deployed parity.
- [ ] Startup work is bounded, read-only, and offline-tolerant.
- [ ] Fresh installation reconstructs the same declared surfaces.
- [ ] Legacy writers are retired after caller migration.
