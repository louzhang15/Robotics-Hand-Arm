# Graph Report - Robotic Hand  (2026-11-23)

> Code-only snapshot of commit `9c915fe25ee0344bc7f009372a07c59809dbc1db`.
> Community names were assigned after reviewing their source symbols.

## Coverage and interpretation limits

- Source: 17 code files scanned; 16 source files have nodes in this snapshot. Documents, PDFs, photos, binary models, local environments,
  credentials and chat logs are outside this automatic index. See
  [the system overview](../PROJECT_MAP.md) for hardware and planned capabilities.
- This Graphify version does not automatically index the Arduino `.ino` sketch
  or OpenSCAD `.scad` models. Their behavior is described separately in the overview.
- The extractor reported a partial parse of `firmware/hand_executor/executor_state.h`
  near line 14. This is a graph-extraction limitation, not a compiler diagnostic.
- Integrity check: no missing/dangling endpoints and no collapsed same-endpoint
  edges in the exported graph; three self-edges remain in C++ test wrappers.
  Inspection shows these wrappers call `state.command`, `state.relax` and
  `state.angle`; those self-edges are name-resolution artifacts, not evidence
  that the wrapper functions recursively call themselves.
- Fifteen links are labelled INFERRED. Treat them as navigation hints to check
  against source. The graph does not prove runtime behavior or hardware readiness.


## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 146 nodes · 243 edges · 10 communities (6 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c915fe2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Manual control and calibration
- Shared imports and test harnesses
- Camera geometry and tracking
- Design and project utilities
- Firmware test bridge
- Serial hand interface
- Executor safety state
- STL mesh inspection
- Firmware assertions
- Serial transport test double

## God Nodes (most connected - your core abstractions)
1. `Hand` - 17 edges
2. `HandTests` - 13 edges
3. `joints_from_landmarks()` - 13 edges
4. `ManualControl` - 11 edges
5. `main()` - 9 edges
6. `CameraGeometryTests` - 7 edges
7. `main()` - 7 edges
8. `Transport` - 6 edges
9. `straight_hand()` - 6 edges
10. `next_targets()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `HandTests` --uses--> `Hand`  [INFERRED]
  tests/test_hand.py → pc/hand.py
- `HandTests` --uses--> `ManualControl`  [INFERRED]
  tests/test_hand.py → pc/control.py
- `main()` --calls--> `Hand`  [EXTRACTED]
  pc/camera.py → pc/hand.py
- `main()` --calls--> `Hand`  [EXTRACTED]
  pc/sliders.py → pc/hand.py
- `main()` --calls--> `ManualControl`  [EXTRACTED]
  pc/sliders.py → pc/control.py

## Import Cycles
- None detected.

## Communities (10 total, 4 thin omitted)

### Community 0 - "Manual control and calibration"
Cohesion: 0.10
Nodes (3): ManualControl, main(), HandTests

### Community 2 - "Camera geometry and tracking"
Cohesion: 0.19
Nodes (9): angle(), draw_landmarks(), joints_from_landmarks(), main(), next_targets(), _norm(), _sub(), CameraGeometryTests (+1 more)

### Community 3 - "Design and project utilities"
Cohesion: 0.17
Nodes (6): main(), gravity_torque_nm(), main(), pulley_radius_mm(), main(), main()

### Community 4 - "Firmware test bridge"
Cohesion: 0.17
Nodes (4): angle(), badCommand(), command(), relax()

### Community 6 - "Executor safety state"
Cohesion: 0.31
Nodes (7): calibrate(), clamp(), command(), finite(), rest(), step(), updateWatchdog()

### Community 7 - "STL mesh inspection"
Cohesion: 0.33
Nodes (3): inspect(), main(), triangles()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Hand` connect `Serial hand interface` to `Manual control and calibration`, `Shared imports and test harnesses`, `Camera geometry and tracking`, `Serial transport test double`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Hand` (e.g. with `HandTests` and `.setUp()`) actually correct?**
  _`Hand` has 3 INFERRED edges - heuristically inferred connections that need verification._
- **Should `Manual control and calibration` be split into smaller, more focused modules?**
  _Cohesion score 0.09538461538461539 - nodes in this community are weakly interconnected._
- **Why does `HandTests` connect `Manual control and calibration` to `Shared imports and test harnesses`, `Serial hand interface`, `Serial transport test double`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `HandTests` (e.g. with `ManualControl` and `Hand`) actually correct?**
  _`HandTests` has 2 INFERRED edges - heuristically inferred connections that need verification._
- **Should `Shared imports and test harnesses` be split into smaller, more focused modules?**
  _Cohesion score 0.09881422924901186 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `Manual control and calibration` to `Design and project utilities`, `Serial hand interface`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._