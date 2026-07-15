# Theoretical project preset

Use for formal models, analytical results, and proof-heavy manuscripts.

## Suggested agents

| Neutral name | Mode | Capabilities | Claude adapter tools | Core responsibility |
|---|---|---|---|---|
| `formalist` | project-write | filesystem read/write | Read, Write, Edit, Glob, Grep | Develop formal definitions and proofs; enforce stated assumptions, complete dependencies, and stable notation. |
| `paper-writer` | project-write | filesystem read/write | Read, Write, Edit, Glob, Grep | Draft the non-technical narrative without weakening or overstating formal results. |

Use `write_policy.git: forbidden`. Keep proof/model ownership with the formalist
and narrative ownership with the paper writer. Both roles must read the shared
notation and assumption registers before editing.

## Suggested commands

| Neutral name | Argument hint | Required process |
|---|---|---|
| `write-section` | section name | Read the model, notation, and dependencies first; reference formal results precisely; verify compilation afterward. |
| `check-proofs` | result name or all | Enumerate assumptions and dependencies, check each step, and report gaps without silently repairing them. |
| `update-state` | phase or component | Use the bundled neutral update-state source unchanged except for project-specific additions. |
