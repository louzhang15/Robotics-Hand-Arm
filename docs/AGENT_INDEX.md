# Agent navigation index

Use the Graphify skill and the current `graphify-out/graph.json` for code first.
`.graphifyrc` defaults to depth 1 and an 800-token target and identifies Arduino
sketches and headers as C++. Generate a missing graph with
`graphify extract . --code-only`; do not load the full JSON/report into context.

For build questions, read only the relevant section below. This pointer table
keeps project documentation discoverable without indexing full documents,
photos, private attachments or chat history. These sources remain authoritative.

| Question | Open this section |
| --- | --- |
| Current arm goal, reach and payload | `docs/ARM_TARGET.md` -> `Agreed scope` |
| What is still unmeasured before buying arm drives? | `docs/ARM_TARGET.md` -> `What still determines the arm hardware` |
| Build order and acceptance gates | `docs/ENGINEERING_PLAN.md` -> `Build sequence and exit conditions` |
| Power budget, tendon radius and arm torque assumptions | `docs/ENGINEERING_PLAN.md` -> `Calculations and corrections`; graph query `gravity_torque_nm()` or `pulley_radius_mm()` |
| Exact servo/horn/insert measurements needed | `docs/MEASUREMENTS.md` -> `Servo and horn` and `Tendon path and printed fits` |
| Firmware protocol, startup defaults, relax, watchdog | `docs/firmware-notes.md` -> `Current behavior`; query `handleLine` and `ExecutorState` |
| Firmware compilation and test command | `docs/firmware-notes.md` -> `Validation` |
| CAD assembly, dimensions and print limitations | `cad/README.md` -> `Seven-cartridge bench integration concept` |
| CAD exports and geometric checks | `cad/README.md` -> `Export commands` and `Validation status` |
| Measured inputs versus planning estimates | `config/measurements.json` (null means unmeasured) |
| Historical verification results and hardware gaps | `docs/BUILD_STATUS.md` -> `Checks` and `Current constraints` |
| Camera model and dependencies | `models/README.md`; graph query `next_targets()` |
| Original requirements, including later autonomy | `docs/PRD.md` -> requested heading only |
| High-level system relationships and planned work | `docs/PROJECT_MAP.md` -> `Current control path` or `Planned expansion` |

Locate a heading with `rg -n '^#' <file>`, then read its line range. Do not read
all linked documents for every task. Use focused `rg` on the specific file for
OpenSCAD modules that the code extractor does not support. Follow source evidence
when graph hints are incomplete or inferred.

Graphify's budget is a target, not a hard output cap in the installed version.
If a query spills, narrow it to a known symbol with `--seed`, use `--context call`
for a call question, or reduce the question scope. A file seed combined with
`--context call` may return only the file node because containment edges are
filtered out; use a symbol seed for call traversal. Do not claim a path exists
merely because search returned neighboring nodes.

## Verified focused lookups

```powershell
graphify query "serial protocol parsing" --seed handleLine --context call --budget 800
graphify query "serial target validation" --seed pc_hand_hand_send --context call --budget 800
graphify query "tracking loss safe pose" --seed "next_targets()" --context call --budget 800
```

On 23 November 2026 these located the actual parser, target validation and
tracking-loss code using 519-942 stdout characters per query, plus 438 stderr
characters of version warnings. These are output-size measurements, not
tokenizer counts or a promised percentage saving. A broad file query exceeded
the requested budget; use focused symbol queries and verify the returned ranges.
