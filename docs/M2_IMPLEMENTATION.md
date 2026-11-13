# Milestone 2 (M2): Implementation, Testing and Demonstration Guide
**Course:** Automata Theory and Computability Simulation Lab  
**Project:** DFA-Min: An Interactive Automata Minimization and State Equivalence Learning Simulator  
**Evaluation Weight:** 9 Marks  

---

## 1. System Implementation Summary
The simulator has been fully implemented using Python (Flask) for the backend automata computations and modern vanilla JavaScript with Cytoscape.js for interactive state diagram visualization.

### Delivered Components:
1. **Interactive DFA Builder & Validation Engine (`automata/dfa.py`):**
   - Formal 5-tuple input $M = (Q, \Sigma, \delta, q_0, F)$.
   - Real-time input validation: non-emptiness, determinism, complete transition functions, valid start and accepting state membership.
   - Breadth-First Search (BFS) reachability traversal to identify disconnected and unreachable states before minimization.
2. **Partition Refinement Minimization Engine (`automata/minimizer.py`):**
   - Initial partition $P_0 = \{F, Q \setminus F\}$.
   - Signature-based partition refinement with step-by-step history logging.
   - Split explanation generation detailing which symbols and target partitions separated each state.
   - Automatic equivalence class detection and minimized DFA construction.
3. **Shortest Distinguishing String Finder (`automata/distinguisher.py`):**
   - BFS exploration over state pairs $(u, v) \in Q \times Q$.
   - Generates minimal-length string $w$ proving non-equivalence: $\delta^*(p, w) \in F \iff \delta^*(q, w) \notin F$.
   - Step-by-step parallel path trace visualizer.
   - Full Myhill-Nerode pairwise distinguishability matrix.
4. **Dual String Simulation & Language Verification (`automata/dfa.py`, `app.py`):**
   - Real-time simulation of input strings on both Original and Minimized DFAs.
   - Trace animation of visited states on Cytoscape.js graphs.
5. **Level 2: Formal Language Equivalence Verifier (`automata/equivalence.py`):**
   - Synchronous product automaton state space exploration.
   - Emptiness check of the symmetric difference: $L(M_1) \triangle L(M_2) = \emptyset$.
   - Counterexample generation if non-equivalent; formal mathematical certificate if equivalent.

---

## 2. Test Suite & Verification Results
Automated unit tests are implemented using **Pytest** with 100% test pass rate.

### Executing Tests:
```powershell
$env:PYTHONPATH="."
python -m pytest tests/ -v
```

### Test Results Summary:
| Test Module | Test Case | Target Feature | Result |
|---|---|---|---|
| `test_dfa.py` | `test_valid_dfa` | Formal validation of complete DFA | PASSED |
| `test_dfa.py` | `test_empty_states` | Empty states error detection | PASSED |
| `test_dfa.py` | `test_invalid_initial_state` | Missing initial state detection | PASSED |
| `test_dfa.py` | `test_invalid_accepting_state` | Non-member accept state detection | PASSED |
| `test_dfa.py` | `test_missing_transition` | Missing transition function check | PASSED |
| `test_dfa.py` | `test_reachability` | BFS unreachable state detection | PASSED |
| `test_dfa.py` | `test_simulation` | Path tracing & string acceptance | PASSED |
| `test_minimizer.py` | `test_textbook_minimization` | Hopcroft 6-state benchmark | PASSED |
| `test_minimizer.py` | `test_already_minimal_dfa` | Irreducible 2-state parity DFA | PASSED |
| `test_minimizer.py` | `test_all_accepting_states` | Single-class collapse | PASSED |
| `test_minimizer.py` | `test_unreachable_state_removal` | Automatic pruning of dead states | PASSED |
| `test_distinguisher.py` | `test_distinguishing_epsilon` | Length-0 distinguishing string ($\epsilon$) | PASSED |
| `test_distinguisher.py` | `test_distinguishing_non_trivial_string` | Minimal distinguishing string discovery | PASSED |
| `test_distinguisher.py` | `test_equivalent_states` | Confirmation of equivalent states | PASSED |
| `test_distinguisher.py` | `test_all_pairs_table` | Distinguishability matrix generation | PASSED |
| `test_equivalence.py` | `test_minimized_equivalence` | Formal proof: $L(M) \equiv L(M')$ | PASSED |
| `test_equivalence.py` | `test_non_equivalent_dfas` | Counterexample discovery | PASSED |

**Total:** 17 Passed, 0 Failed, 0 Skipped (100% Pass Rate).

---

## 3. Demonstration Script for Team Presentation

### Step 1: Launch the Simulator
Run launcher script:
```powershell
python run.py
```
The browser will automatically open at `http://127.0.0.1:5000`.

### Step 2: Textbook Benchmark Demonstration (Member 1 & 2)
1. Select the **Textbook 6-State DFA (Hopcroft Example)** preset.
2. Point out the formal specification $M = (Q, \Sigma, \delta, q_0, F)$ in the left panel.
3. Click **"Validate & Run"** to render the original Cytoscape.js graph.
4. Show the **Metrics Row**: 6 Original States $\to$ 4 Minimized States (33% state space reduction).

### Step 3: Step-by-Step Stepper (Member 2 & 3)
1. In the **Step-by-Step Partition Refinement Workspace**, click **"Reset"** to inspect $P_0 = \{\{C, D\}, \{A, B, E, F\}\}$.
2. Click **"Next Step"**: Show how Block $\{A, B, E, F\}$ splits because $A, B$ transition to $\{C, D\}$ on symbol `1`, whereas $E, F$ do not.
3. Show the **dynamic node coloring** on the Cytoscape canvas matching partition blocks.
4. Click **"Play"** with the speed slider to auto-step until the stable fixed-point is reached.
5. Inspect the constructed **Minimized DFA** state diagram.

### Step 4: Distinguishing Strings (Member 4)
1. Switch to the **"⚡ Distinguishing Strings"** tab.
2. Select State $A$ and State $C$. Click **"Find Distinguishing String"**:
   - Result: Distinguished by $\epsilon$ (empty string, length 0) because $C$ is accepting and $A$ is non-accepting.
3. Select State $A$ and State $E$. Click **"Find Distinguishing String"**:
   - Result: Distinguished by `"1"`: $\delta^*(A, 1) = C$ (Accepting), while $\delta^*(E, 1) = F$ (Rejecting).
4. Click **"Compute All Pairs Table"** to display the complete Myhill-Nerode distinguishability matrix.

### Step 5: String Testing & Formal Proof (Member 4 & 5)
1. Switch to the **"🧪 String Testing & Proof"** tab.
2. Enter string `0101` and click **"Run Simulation on Both DFAs"**:
   - Show parallel animation on both graphs.
   - Show status: `ACCEPTED` on both, verifying consistency.
3. Click **"Run Formal Product Automaton Verification"**:
   - Show the **Mathematical Proof Certificate**:
     Explored product state space: 8 reachable pairs out of 24 theoretical bound.
     $L(M_1) \triangle L(M_2) = \emptyset$ is formally proven.
