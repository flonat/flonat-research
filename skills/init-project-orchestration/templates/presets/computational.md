# Computational project preset

Use when software, algorithms, simulations, or experiments are themselves the
research contribution.

## Suggested agents

| Neutral name | Mode | Capabilities | Claude adapter tools | Core responsibility |
|---|---|---|---|---|
| `code-architect` | project-write | filesystem read/write, shell | Read, Write, Edit, Bash | Design and implement the core library with typed interfaces, tests, and documented dependency changes. |
| `experiment-runner` | project-write | filesystem read/write, shell | Read, Write, Edit, Bash | Run versioned configurations with fixed seeds; preserve raw run output, logs, and summaries. |
| `paper-writer` | project-write | filesystem read/write | Read, Write, Edit, Glob, Grep | Draft from exported results and keep code/result/paper claims aligned. |

Use `write_policy.git: forbidden` unless the user explicitly expands a role.
Separate core-code ownership from experiment execution. If the project requires
large sweeps or GPU work, follow the canonical HPC guide and keep every Avon
workflow in a named remote tmux session.

## Suggested commands

| Neutral name | Argument hint | Required process |
|---|---|---|
| `run-experiment` | config or experiment description | Resolve a versioned config; run through `uv`; record seed, revision, logs, and output paths. |
| `run-tests` | test selection | Run the smallest relevant suite, report exact failures, and update state only when test status changes. |
| `create-figure` | figure description | Generate from versioned experiment output and verify labels, units, and reproducibility. |
| `write-section` | section name | Draft from verified experiment artifacts; never infer absent results. |
| `update-state` | phase or component | Use the bundled neutral update-state source unchanged except for project-specific additions. |
