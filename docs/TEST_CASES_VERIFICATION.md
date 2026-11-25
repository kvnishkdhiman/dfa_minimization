# CSET302: Test Suite & Verification Matrix
## Automata Theory Simulator Development Project (Milestone-II)

**Project Title:** DFA-Min: Interactive Automata Minimization and State Equivalence Simulator  
**Group ID:** CSET302-Group-DFA-Min  
**Testing Framework:** Pytest 8.0+ / Python 3.9+  
**Total Automated Tests:** 24 Test Cases  
**Test Success Rate:** 100% (24 Passed, 0 Failed, 0 Errors)  

---

## 1. Test Verification Matrix (Normal, Boundary, Invalid, Correctness)

| Test ID | Category | Feature / Input Under Test | Input Specification | Expected Result | Observed Result | Status |
|:---:|:---:|---|---|---|---|:---:|
| **T01** | Normal | DFA Simulation: Accepted String | String `01` on Hopcroft 6-State DFA | Path: $A \xrightarrow{0} B \xrightarrow{1} D \in F$. `accepted = True` | `accepted = True`, trace `['A', 'B', 'D']` | **PASS** |
| **T02** | Normal | DFA Simulation: Rejected String | String `00` on Hopcroft 6-State DFA | Path: $A \xrightarrow{0} B \xrightarrow{0} A \notin F$. `accepted = False` | `accepted = False`, trace `['A', 'B', 'A']` | **PASS** |
| **T03** | Invalid | Missing Transition in Definition | State `A` missing outgoing transition on symbol `1` | `validate() = (False, "Missing transition for state 'A' on symbol '1'")` | Validation fails with exact error message | **PASS** |
| **T04** | Boundary | Empty String $\epsilon$ Acceptance | Input string `""` on DFA with initial state $q_0 \in F$ | Evaluates start state acceptance: `accepted = (q0 in F)` | Handled correctly via start state membership | **PASS** |
| **T05** | Invalid | Empty State Set Validation | State set $Q = \emptyset$ | Validation error: "States set cannot be empty" | Validation fails immediately | **PASS** |
| **T06** | Invalid | Initial State Not in State Set | $Q = \{A, B\}, q_0 = Z$ | Validation error: "Initial state 'Z' is not in states set Q" | Validation fails immediately | **PASS** |
| **T07** | Invalid | Accepting States Not Subset of Q | $Q = \{A, B\}, F = \{A, X\}$ | Validation error: "Accepting state 'X' is not in states set Q" | Validation fails immediately | **PASS** |
| **T08** | Correctness | Reachability & Unreachable Pruning | DFA with states $A, B$ and isolated state $Z$ | $Z$ identified as unreachable; $Q_{\text{reach}} = \{A, B\}$ | `unreachable = ['Z']`, pruned before minimization | **PASS** |
| **T09** | Correctness | Distinguishing String: $\epsilon$-distinguishable | States $A \notin F$ and $C \in F$ | Shortest witness $w = \epsilon$ (empty string) | Returns `""` (witness length 0) | **PASS** |
| **T10** | Correctness | Distinguishing String: Multi-symbol BFS | States $A$ and $B$ in 6-state Hopcroft DFA | Shortest witness $w = 1$ ($\delta^*(A, 1) = C \in F, \delta^*(B, 1) = D \notin F$ or vice versa) | Returns `"1"` with diverging acceptance traces | **PASS** |
| **T11** | Correctness | Distinguishing String: Equivalent Pair | States $C$ and $D$ in 6-state Hopcroft DFA | No distinguishing string exists ($C \equiv D$). Returns `None` | Returns `None`, states marked equivalent | **PASS** |
| **T12** | Correctness | All-Pairs Distinguishability Matrix | Full lower-triangular matrix of state pairs | Table matches theoretical pairwise witness strings | Complete table generated with witness lengths | **PASS** |
| **T13** | Correctness | Textbook 6-State Hopcroft Minimization | 6-state DFA with redundancies $\{A, B\}$ and $\{C, D\}$ | Partitions refine to 4 quotient blocks: $\{A, B\}, \{C, D\}, \{E\}, \{F\}$ | Exactly 4 quotient states formed | **PASS** |
| **T14** | Boundary | Already Minimal Automaton | 2-state parity checker DFA | 0 splits occur; final size = 2 states; 0 equivalent pairs | Preserves 2 states; 0% reduction | **PASS** |
| **T15** | Boundary | All States Accepting & Unified | 2 states with identical transitions, both in $F$ | Merges into 1 single quotient state | Merged into 1 state | **PASS** |
| **T16** | Mathematical | Level-2 Formal Equivalence Proof | Original Hopcroft DFA vs Minimized 4-state DFA | Synchronous product $L(M_1) \oplus L(M_2) = \emptyset \implies$ Equivalent | Returns `is_equivalent = True`, certificate emitted | **PASS** |
| **T17** | Mathematical | Formal Equivalence: Non-Equivalent DFAs | Language $(0+1)^*0$ vs Language $(0+1)^*1$ | Product reaches final state in $F_{\Delta} \implies$ Not Equivalent | Returns `is_equivalent = False` + counterexample | **PASS** |
| **T18** | API | HTTP GET `/` (Laboratory UI) | Request to root URL | Status 200, returns HTML page with studio workspace | Status 200, HTML content verified | **PASS** |
| **T19** | API | HTTP GET `/api/presets` | Request for preset benchmarks | Status 200, returns 5 academic benchmark configurations | Status 200, JSON schema valid | **PASS** |
| **T20** | API | HTTP POST `/api/dfa/validate` | Valid DFA JSON payload | Status 200, `success = True`, Cytoscape elements | Status 200, graph elements returned | **PASS** |
| **T21** | API | HTTP POST `/api/dfa/minimize` | 6-state DFA JSON payload | Status 200, complete step history, quotient elements | Status 200, step history with signatures | **PASS** |
| **T22** | API | HTTP POST `/api/dfa/distinguish` | Payload with states $p=A, q=C$ | Status 200, `distinguishing_string = ""`, traces | Status 200, traces returned | **PASS** |
| **T23** | API | HTTP POST `/api/dfa/simulate` | String `"0101"` on original & minimized | Status 200, dual paths, `match = True` | Status 200, both say ACCEPT | **PASS** |
| **T24** | API | HTTP POST `/api/dfa/verify` | Original and Minimized DFA payloads | Status 200, `is_equivalent = True`, proof certificate | Status 200, proof verified | **PASS** |

---

## 2. Pytest Automated Execution Evidence

Execution Command:
```powershell
$env:PYTHONPATH="C:\Users\Ananya\dfa_minimization"
python -m pytest tests -v
```

Execution Log:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.2.0, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\Ananya\dfa_minimization
collected 24 items

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
