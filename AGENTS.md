# Robotic Hand + Arm: shared agent workflow

Use these rules in the same checkout from Codex and Claude Code. Use the
installed Graphify skill for navigation; the graph is an index, not source truth.

## Find before reading

1. Check `git status --short` and use the live `graphify-out/graph.json`.
   If it is missing, run `graphify extract . --code-only` from this root.
2. For code questions, query before opening source:
   `graphify query "<focused question>" --budget 800 --depth 1 --context call`.
   Omit or change the context filter when looking for imports or containment.
3. Narrow noisy results with a specific symbol `--seed`, `graphify path`, or
   `graphify explain`. File seeds with `--context call` can hide containment;
   use symbol seeds for calls and unfiltered file seeds only for discovery.
   The installed CLI can exceed its requested budget; narrow the query instead
   of loading the oversized answer. Budget figures do not include CLI warnings.
4. Open only returned source files and the line ranges needed to verify the
   result, then read the related tests needed for the change. Do not dump the
   graph JSON, full reports, every source file, or whole build plans into context.
5. For hardware, CAD, requirements and build-document questions, use the compact
   `docs/AGENT_INDEX.md` to choose the relevant file/section. Do not automatically
   index ordinary non-code work, photos, PDFs or private attachments.
6. If Graphify has no useful result, use one focused `rg` lookup and verify its
   source. Name the indexing gap; never invent a dependency or claim full coverage.

## Keep the index useful

- Run `graphify update .` after each batch of code edits and before handoff.
  Do not rely on a hook that is unavailable, has not run, or is awaiting trust.
- Query the live local graph, not `docs/graph/graph.json`; that is a published
  snapshot for sharing. Refresh published views only when requested or relevant.
- Keep `.graphifyignore` exclusions: generated maps must not index themselves.
  Keep credentials, private chat logs, query histories and local caches out of Git
  and the graph. Do not install new hooks or tools merely to answer a query.
- Delegate independent work when useful. Give subagents the focused question,
  relevant paths and evidence rather than a full graph/report dump; verify results.

## Project boundaries and checks

- Target: manually pick up and move a pen with about 300 mm reach. Details and
  remaining assumptions are in `docs/ARM_TARGET.md`; the robot is hardware-untested.
- `.graphifyrc` indexes Arduino `.ino` files and headers as C++. Verify inferred
  links against source; C++ name resolution can still be wrong. OpenSCAD is not
  automatically indexed; use the document index and a focused module lookup.
- Software verification: `python -m unittest discover -s tests -v`.
  Compile-only firmware check: `arduino-cli compile --fqbn esp32:esp32:esp32s3
  --build-path build/firmware firmware/hand_executor` (one command).
- Report what changed, the checks actually run and remaining limits. A graph,
  passing software tests or CAD topology checks do not establish physical readiness.
