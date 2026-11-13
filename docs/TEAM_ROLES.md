# DFA-Min: Five-Member Team Division & Responsibilities

This document defines the roles, modules, and evaluation tasks for each of the 5 team members on the **DFA-Min** project.

---

## Member 1 — DFA Input Specification & Validation
- **Assigned Module:** `automata/dfa.py` (Validation & Parsing), `templates/index.html` (Input Panel)
- **Key Responsibilities:**
  1. Design user interface for DFA formal 5-tuple input: $M = (Q, \Sigma, \delta, q_0, F)$.
  2. Implement dynamic transition table matrix generation based on states and alphabet.
  3. Validate input completeness, determinism, unique state names, alphabet coverage, and valid initial/accepting states.
  4. Implement JSON serialization and deserialization for DFA presets and custom configurations.
  5. Provide clear, helpful error messages when input violates DFA requirements.

---

## Member 2 — Core Minimization Algorithm & Reachability
- **Assigned Module:** `automata/minimizer.py`, `automata/dfa.py` (BFS Reachability)
- **Key Responsibilities:**
  1. Implement graph reachability analysis (BFS from initial state $q_0$) to identify and prune unreachable states.
  2. Implement the Partition Refinement Algorithm (Moore / Hopcroft):
     - Initial partition: $P_0 = \{F, Q \setminus F\}$.
     - Iterative signature computation for states on input symbols.
     - Block splitting and termination detection when fixed-point stability is reached.
  3. Record complete history of partitions, sub-blocks, and mathematical split explanations for each step.
  4. Construct the minimal equivalent DFA from the final equivalence classes.

---

## Member 3 — Interactive Graph Visualization & Animation
- **Assigned Module:** `static/js/visualizer.js`, Cytoscape.js integration
- **Key Responsibilities:**
  1. Configure Cytoscape.js graph canvas, styles, and layouts (Circle, Breadthfirst, Force-directed CoSE).
  2. Visually distinguish state properties: initial state (purple accent), accepting states (double circle), unreachable states (red dashed / dimmed).
  3. Render dynamic state merging: color-code states belonging to the same partition using vibrant distinct palettes.
  4. Implement interactive graph controls (zoom in, zoom out, fit-to-view, draggable nodes).
  5. Animate simulation traces and state-traversal paths on the graph canvas.

---

## Member 4 — Equivalence Verification & Distinguishing Strings
- **Assigned Module:** `automata/distinguisher.py`, `automata/equivalence.py`, `tests/`
- **Key Responsibilities:**
  1. Implement Shortest Distinguishing String Finder using BFS over state pairs in the cross-product graph.
  2. Generate step-by-step parallel trace comparing how string $w$ leads one state to accept and the other to reject.
  3. Implement Myhill-Nerode pairwise distinguishability matrix for all state pairs.
  4. Implement Level 2 Formal Language Equivalence Checker via synchronous product automaton ($M_1 \times M_2$) state space exploration.
  5. Author and maintain the automated Pytest test suite covering edge cases and corner cases.

---

## Member 5 — Frontend Integration, UI/UX & Documentation
- **Assigned Module:** `static/css/style.css`, `static/js/app.js`, `docs/`, `run.py`
- **Key Responsibilities:**
  1. Design modern, responsive dark-slate UI with tabs, metrics cards, badges, and smooth transitions.
  2. Integrate frontend components with Flask REST API endpoints.
  3. Implement partition refinement playback stepper (Next, Prev, Play, Pause, Speed Slider, Jump to End).
  4. Manage project documentation, Milestone 1 design specifications, and Milestone 2 demonstration assets.
  5. Coordinate live presentation and team rehearsal for evaluation.
