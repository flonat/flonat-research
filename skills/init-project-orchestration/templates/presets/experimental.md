# Experimental project preset

Use for data collection, cleaning, causal inference, and econometric analysis.
Populate every path and standard from the project rather than copying generic
placeholders.

## Suggested agents

| Neutral name | Mode | Capabilities | Claude adapter tools | Core responsibility |
|---|---|---|---|---|
| `data-engineer` | project-write | filesystem read/write, shell | Read, Write, Edit, Bash | Transform `data/raw/` read-only inputs into documented `data/processed/` outputs; validate merges, missingness, and duplicates. |
| `econometrician` | project-write | filesystem read/write, shell | Read, Write, Edit, Bash | Run the locked specification and robustness checks; export tables and figures rather than hard-coding results. |
| `paper-writer` | project-write | filesystem read/write | Read, Write, Edit, Glob, Grep | Draft project prose from verified outputs while preserving notation and citation conventions. |

Use `write_policy.git: forbidden` for all three. Give the data engineer an
explicit `data/raw/` prohibition. Give the econometrician processed-data read
ownership and output-only write ownership. The paper writer must not execute
analysis or invent values.

## Suggested commands

| Neutral name | Argument hint | Required process |
|---|---|---|
| `clean-data` | dataset or transformation | Read the locked data contract; leave `data/raw/` untouched; write and validate a reproducible processed output. |
| `run-regression` | specification | Confirm the locked estimand before estimates; run through `uv`; export N, uncertainty, diagnostics, and clustering details. |
| `create-figure` | figure description | Read generated data/results; create a reproducible vector figure; verify labels, units, and source script. |
| `write-section` | section name | Read project guidance, notation, bibliography, and generated outputs; draft without hard-coded computed results. |
| `update-state` | phase or component | Use the bundled neutral update-state source unchanged except for project-specific additions. |
