# DFA-Min: Interactive Automata Minimization and State Equivalence Simulator
**Group ID:** CSET302-Group-DFA-Min  
**Course:** CSET302 – Automata Theory and Computability  
**Milestone:** Milestone-II: Final Simulator Demonstration & Evaluation (23–27 November 2026)  
**Authors:** Ananya and Team (5 Members)  
**Faculty Evaluator:** Course Faculty, School of Computer Science & Engineering  

---

## Overview: What does the simulator do?
**DFA-Min** is a full-featured, interactive educational web simulator designed to demonstrate the minimization of Deterministic Finite Automata (DFAs) using the **Partition Refinement Algorithm** (Moore / Hopcroft). The tool addresses the core educational difficulty students face when computing quotient automata manually: understanding why states split, tracking successor transition signatures, discovering distinguishing strings, and verifying that the minimized automaton preserves the exact recognized language $L(M)$.

The simulator validates user-defined automata, prunes unreachable states via Breadth-First Search (BFS), executes step-by-step partition refinement with live successor signature analysis, discovers shortest witness distinguishing strings for non-equivalent state pairs, and provides formal mathematical proof of language equivalence via the synchronous product automaton $M_1 \times M_2$.

---

## Supported features: list implemented operations
1. **Interactive DFA Specification & Matrix Editor:**
   - Define custom DFAs via formal 5-tuple: $M = (Q, \Sigma, \delta, q_0, F)$.
   - Dynamic, auto-resizing transition matrix table $\delta(q, a)$ supporting arbitrary alphabets and state names.
   - 5 built-in academic benchmark presets (Textbook 6-State Hopcroft, Unreachable States DFA, 8-State Redundant DFA, Parity Checker Irreducible DFA, Substring '01' DFA).
2. **Deterministic Input Validation:**
   - Real-time syntax and semantic validation (non-empty state set, alphabet uniqueness, single initial state $q_0 \in Q$, accepting states subset $F \subseteq Q$, complete transition coverage).
   - Clear diagnostic error messages for missing or ambiguous transitions.
3. **Graph Reachability Analysis (BFS):**
   - Automatically detects and prunes dead/unreachable states prior to minimization.
   - Renders unreachable states with distinct dashed-red borders and warning alerts.
4. **Step-by-Step Partition Refinement Stepper (5-Stage Lifecycle):**
   - Breadcrumb lifecycle indicator: `Reachability (BFS)` $\rightarrow$ `Initial P₀` $\rightarrow$ `Signature Splitting` $\rightarrow$ `Fixed Point` $\rightarrow$ `Merged Quotient DFA`.
   - VCR playback controls: **Reset**, **Previous Step**, **Next Step**, **Auto-Play**, **Jump to End**, and variable speed slider (400ms – 2500ms).
   - Dynamic block chips with strict semantic colors (Block 0 = Blue, Block 1 = Green).
5. **Successor-Block Signature Analysis Table (Textbook Whiteboard Proof):**
   - Per-round dynamic table computing $\text{sig}(q) = (\text{block}(\delta(q, a)))_{a \in \Sigma}$.
   - Pinpoints exact split causes when signatures diverge; shows group unification when matching.
   - State-hover cross-highlighting with the Cytoscape.js state diagram.
6. **Shortest Distinguishing String Synthesis (Myhill-Nerode Witness):**
   - Interactive pair selector $(p, q)$ finding the minimal length string $w \in \Sigma^*$ such that $\delta^*(p, w) \in F \oplus \delta^*(q, w) \in F$ via BFS on state pairs.
   - Side-by-side transition trace paths showing divergent acceptance outcomes.
   - Full lower-triangular all-pairs distinguishability matrix.
7. **Empirical Dual-Automata String Simulation (Level 1 Testing):**
   - Simultaneous path execution comparing Original DFA vs Minimized DFA on any arbitrary input string.
   - Visual path animation and instant acceptance agreement check.
8. **Formal Language Equivalence Proof (Level 2 Mathematical Proof):**
   - Synchronous product automaton exploration $M_1 \times M_2$.
   - Computes symmetric difference language $L_{\Delta} = L(M_1) \oplus L(M_2)$.
   - Generates formal verification certificate confirming $L(M_{\text{orig}}) \equiv L(M_{\text{min}})$ for all infinite strings in $\Sigma^*$.
9. **Interactive State Diagram Visualization (Cytoscape.js):**
   - Initial State: Royal Blue fill (`#1d4ed8`) + Cyan border (`#38bdf8`, 3.5px).
   - Accepting States: Deep Green fill (`#064e3b`) + Double Circle border (`#10b981`, 7px).
   - Unreachable States: Crimson fill (`#2e080b`) + Dashed Red border (`#ef4444`).
   - Active/Highlighted: Golden Yellow (`#fbbf24`).
   - Circle, Breadth-First tree, and physics-based CoSE force layouts.

---

## Technology stack and dependencies: versions
- **Runtime Environment:** Python 3.9+ (Tested on Python 3.10, 3.11, 3.12, 3.14 on Windows, Linux, macOS)
- **Web Backend Framework:** Flask 3.0.0+ (RESTful JSON API architecture)
- **Testing Framework:** Pytest 8.0.0+ / Pytest 9.2.0 (24 automated test cases)
- **Frontend Architecture:** Vanilla JavaScript (ES6+ modular, no heavy frontend frameworks required)
- **Styling:** Custom CSS3 with Cyber-Academic Obsidian & Golden Yellow gradient theme
- **Graph Visualization:** Cytoscape.js 3.28.1 (Interactive canvas, bezier directed edges, dynamic styling)
- **Typography:** Google Fonts (Plus Jakarta Sans, Inter, Fira Code monospace)

---

## Installation: numbered setup commands
Clone the repository or navigate to the project directory:

```bash
# 1. Open terminal and navigate to the project directory
cd "C:\Users\Ananya\dfa_minimization"

# 2. (Optional but recommended) Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install required Python packages
pip install -r requirements.txt
```

---

## How to run: exact command and entry point
Start the Flask application server:

```bash
# Entry point option A (Standard):
python app.py

# Entry point option B (Auto-browser launcher):
python run.py
```

The application will start on:  
**`http://127.0.0.1:5000`** (or `http://localhost:5000`)

Open your web browser and navigate to the URL to begin simulation.

---

## Example: sample automaton definition, input and output

### 1. Sample Automaton (Textbook 6-State Hopcroft DFA)
- **States $Q$:** `A, B, C, D, E, F`
- **Alphabet $\Sigma$:** `0, 1`
- **Initial State $q_0$:** `A`
- **Accepting States $F$:** `C, D`
- **Transition Function $\delta$:**
  - $\delta(A, 0) = B$, $\delta(A, 1) = C$
  - $\delta(B, 0) = A$, $\delta(B, 1) = D$
  - $\delta(C, 0) = E$, $\delta(C, 1) = F$
  - $\delta(D, 0) = E$, $\delta(D, 1) = F$
  - $\delta(E, 0) = E$, $\delta(E, 1) = F$
  - $\delta(F, 0) = F$, $\delta(F, 1) = E$

### 2. Execution Traces & Outputs
- **Step 0 ($P_0$):** Divided into non-accepting $P_0 = \{A, B, E, F\}$ and accepting $P_1 = \{C, D\}$ ($\epsilon$-distinguishable).
- **Step 1 ($P_1$):** Signatures computed for $P_0$:
  - $A \rightarrow (P_0, P_1)$, $B \rightarrow (P_0, P_1)$ (stay together)
  - $E \rightarrow (P_0, P_0)$, $F \rightarrow (P_0, P_0)$ (stay together)
  - Block $P_0$ splits into $\{A, B\}$ and $\{E, F\}$!
- **Step 2 ($P_2$):** Signatures for $\{E, F\}$ computed on alphabet $\{0, 1\}$. $E \rightarrow (E, F)$ and $F \rightarrow (F, E)$ diverge $\rightarrow$ Block splits into $\{E\}$ and $\{F\}$.
- **Step 3 (Fixed Point):** Partitions $\{ \{A, B\}, \{C, D\}, \{E\}, \{F\} \}$ are stable.
- **Minimized DFA Output:** 4 quotient states (`[A, B]`, `[C, D]`, `[E]`, `[F]`). State space reduced by 33.3%.
- **Distinguishing String:** Pair $(A, C)$ distinguished by shortest string $w = 1$ ($\delta^*(A, 1) = C \in F$, $\delta^*(C, 1) = F \notin F$).
- **Equivalence Verification:** Symmetric difference $L_{\Delta} = \emptyset$ $\rightarrow$ Formally Proven Equivalent!

---

## Project structure: modules and responsibilities
```
dfa_minimization/
├── app.py                     # Main Flask Application Server & REST API endpoints
├── run.py                     # CLI launcher with automatic browser opening
├── requirements.txt           # Python package dependencies (Flask, pytest)
├── README.md                  # Complete technical specification and guide
├── automata/                  # Core Automata Theory Computation Engine
│   ├── __init__.py            # Package initialisation
│   ├── dfa.py                 # DFA data structure, validation, reachability BFS, simulation
│   ├── minimizer.py           # Moore / Hopcroft Partition Refinement algorithm
│   ├── distinguisher.py       # Myhill-Nerode Shortest Distinguishing String Finder (BFS)
│   └── equivalence.py         # Synchronous Product Automaton & Symmetric Difference Proof
├── static/                    # Frontend Client Assets
│   ├── css/
│   │   └── style.css          # Cyber-academic Obsidian & Gold design system
│   └── js/
│       ├── presets.js         # Built-in educational DFA benchmark suites
│       ├── visualizer.js      # Cytoscape.js graph controller & semantic color engine
│       └── app.js             # UI controller, stepper logic, dynamic signature tables
├── templates/
│   └── index.html             # Single-page laboratory application template
├── tests/                     # Automated Pytest Verification Suite
│   ├── __init__.py            # Test package marker
│   ├── test_dfa.py            # DFA model, validation, and reachability tests
│   ├── test_minimizer.py      # Partition refinement and state reduction tests
│   ├── test_distinguisher.py  # Distinguishing string discovery and table tests
│   ├── test_equivalence.py    # Product automaton language equivalence tests
│   └── test_api.py            # Flask REST API endpoints integration tests
└── docs/                      # Formal Academic & Milestone Documentation
    ├── M1_DESIGN_DOCUMENT.md  # Milestone 1 Architecture & Design Specification
    ├── M2_IMPLEMENTATION.md   # Milestone 2 Implementation & Verification Report
    ├── TEAM_ROLES.md          # 5-Member Team Allocation & Viva Reference Guide
    └── TEST_CASES_VERIFICATION.md # Comprehensive T01-T15 Verification Matrix
```

---

## Testing: command, test data and expected behavior
The test suite consists of **24 automated tests** covering unit operations, edge cases, corner cases, and API integration.

### Run All Tests:
```powershell
# Set PYTHONPATH and execute pytest
$env:PYTHONPATH="C:\Users\Ananya\dfa_minimization"
python -m pytest tests -v
```

### Test Suite Summary:
```text
tests/test_api.py::test_index_route                     PASSED [  4%]
tests/test_api.py::test_presets_route                   PASSED [  8%]
tests/test_api.py::test_validate_api                   PASSED [ 12%]
tests/test_api.py::test_minimize_api                   PASSED [ 16%]
tests/test_api.py::test_distinguish_api                PASSED [ 20%]
tests/test_api.py::test_simulate_api                   PASSED [ 25%]
tests/test_api.py::test_verify_equivalence_api         PASSED [ 29%]
tests/test_dfa.py::test_valid_dfa                      PASSED [ 33%]
tests/test_dfa.py::test_empty_states                   PASSED [ 37%]
tests/test_dfa.py::test_invalid_initial_state          PASSED [ 41%]
tests/test_dfa.py::test_invalid_accepting_state        PASSED [ 45%]
tests/test_dfa.py::test_missing_transition             PASSED [ 50%]
tests/test_dfa.py::test_reachability                   PASSED [ 54%]
tests/test_dfa.py::test_simulation                     PASSED [ 58%]
tests/test_distinguisher.py::test_distinguishing_eps   PASSED [ 62%]
tests/test_distinguisher.py::test_distinguishing_str   PASSED [ 66%]
tests/test_distinguisher.py::test_equivalent_states    PASSED [ 70%]
tests/test_distinguisher.py::test_all_pairs_table      PASSED [ 75%]
tests/test_equivalence.py::test_minimized_equivalence  PASSED [ 79%]
tests/test_equivalence.py::test_non_equivalent_dfas   PASSED [ 83%]
tests/test_minimizer.py::test_textbook_minimization    PASSED [ 87%]
tests/test_minimizer.py::test_already_minimal_dfa      PASSED [ 91%]
tests/test_minimizer.py::test_all_accepting_states     PASSED [ 95%]
tests/test_minimizer.py::test_unreachable_removal      PASSED [100%]
============================== 24 passed in 0.35s ==============================
```

---

## Known limitations and troubleshooting
1. **Scope Limitation (By Design):** The simulator focuses strictly on Deterministic Finite Automata (DFAs). Non-Deterministic Automata (NFA), $\epsilon$-NFAs, and Pushdown Automata (PDA) are outside the project scope to guarantee deep, rigorous DFA minimization visualization.
2. **Alphabet Size:** The interactive transition matrix is optimized for practical alphabet sizes ($|\Sigma| \le 10$). Larger alphabets will require horizontal scrolling.
3. **Graph Overlap on Very Large DFAs:** For DFAs with $> 25$ states, the Circle layout provides the clearest visual presentation; the Force-directed layout can be toggled using the toolbar button `Force`.
4. **Port 5000 Collision Troubleshooting:** If port 5000 is occupied by another application, run with:
   `python -c "from app import app; app.run(port=5050)"`

---

## Team contributions and acknowledgements

| Member | Assigned Role & Module | Primary Responsibilities & Code Delivered |
|---|---|---|
| **Member 1** | DFA Input & Validation | Form validation, dynamic transition matrix, schema parsing, JSON serialization (`automata/dfa.py`, `app.js`). |
| **Member 2** | Core Minimization Engine | Reachability BFS, Partition Refinement engine, signature calculations, quotient DFA builder (`automata/minimizer.py`). |
| **Member 3** | Graph Visualization | Cytoscape.js integration, semantic color system (Blue initial, Green double circle), layouts, animations (`visualizer.js`). |
| **Member 4** | Verification & Testing | Shortest distinguishing string BFS, product automaton equivalence proof, 24 Pytest unit/integration tests (`distinguisher.py`, `equivalence.py`, `tests/`). |
| **Member 5** | Frontend Integration & UX | Flask REST API routing, Stepper controller, 5-stage lifecycle bar, textbook signature tables, report & docs (`app.py`, `style.css`, `index.html`). |

### Acknowledgements
We express our sincere gratitude to our course faculty for their continuous guidance throughout CSET302 Automata Theory and Computability. Theoretical principles are grounded in standard literature by Hopcroft, Motwani, & Ullman (2006) and Sipser (2013).
