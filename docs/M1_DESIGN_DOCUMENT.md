# Milestone 1 (M1): Simulator Design Document
**Course:** Automata Theory and Computability Simulation Lab  
**Project:** DFA-Min: An Interactive Automata Minimization and State Equivalence Learning Simulator  
**Evaluation Weight:** 5 Marks  

---

## 1. Problem Statement & Educational Objectives
A Deterministic Finite Automaton (DFA) recognized in formal language theory often contains redundant or unreachable states. DFA minimization computes the unique minimal automaton that recognizes the exact same regular language $L(M)$.

While the Partition Refinement Algorithm (Moore, Hopcroft) is standard in theoretical computer science, students frequently struggle with:
1. Understanding why two states can or cannot be merged.
2. Manually calculating partition splits without making indexing or symbol errors.
3. Distinguishing reachable state sets from dead or unreachable states.
4. Verifying whether the resulting minimized DFA truly recognizes the exact same language.

**DFA-Min** solves this problem by providing an interactive, visual laboratory that executes step-by-step partition refinement, visually traces outgoing transition signatures, finds shortest distinguishing strings for distinguishable pairs, and generates formal product-automaton equivalence certificates.

---

## 2. Formal Mathematical Specification of DFA
A Deterministic Finite Automaton is formally defined as a 5-tuple:
$$M = (Q, \Sigma, \delta, q_0, F)$$

Where:
- $Q$: Finite, non-empty set of states.
- $\Sigma$: Finite, non-empty input alphabet.
- $\delta: Q \times \Sigma \to Q$: Total transition function mapping each (state, symbol) pair to a unique destination state.
- $q_0 \in Q$: Designated initial/start state.
- $F \subseteq Q$: Set of accepting/final states.

The extended transition function $\delta^*: Q \times \Sigma^* \to Q$ is defined inductively:
1. $\delta^*(q, \epsilon) = q$
2. $\delta^*(q, wa) = \delta(\delta^*(q, w), a)$ for all $w \in \Sigma^*, a \in \Sigma$.

A string $w \in \Sigma^*$ is accepted by $M$ if $\delta^*(q_0, w) \in F$. The language recognized by $M$ is:
$$L(M) = \{w \in \Sigma^* \mid \delta^*(q_0, w) \in F\}$$

---

## 3. Core Algorithm: Partition Refinement
Two states $p, q \in Q$ are **equivalent** ($p \equiv q$) if:
$$\forall w \in \Sigma^*, \quad \delta^*(p, w) \in F \iff \delta^*(q, w) \in F$$

Two states are **k-equivalent** ($p \equiv_k q$) if no string of length $\le k$ can distinguish them.

### Algorithm Pseudocode:
```text
Algorithm: PartitionRefinement(DFA M)
Input: DFA M = (Q, Σ, δ, q0, F)
Output: Minimized DFA M' = (Q', Σ, δ', [q0], F')

1. Q_reach = ReachableStates(M, q0) using BFS/DFS
2. If F ∩ Q_reach == ∅ or Q_reach \ F == ∅:
     P_0 = [Q_reach]
   Else:
     P_0 = [F ∩ Q_reach, Q_reach \ F]
3. k = 0
4. Repeat:
     P_{k+1} = []
     For each block B in P_k:
       Partition states in B into sub-blocks such that:
         s1, s2 ∈ B are in the same sub-block iff
         ∀ a ∈ Σ, block_index(δ(s1, a), P_k) == block_index(δ(s2, a), P_k)
       Add all resulting sub-blocks to P_{k+1}
     k = k + 1
   Until |P_k| == |P_{k-1}|   // Stable fixed point reached
5. P_final = P_k
6. Construct M':
     - States Q' = { [q] | [q] ∈ P_final }
     - Start state q0' = [q0]
     - Final states F' = { [q] ∈ P_final | [q] ∩ F ≠ ∅ }
     - Transition function: δ'([q], a) = [δ(q, a)] for any q ∈ [q]
7. Return M'
```

---

## 4. Manually Solved Benchmark Example
Consider the textbook 6-state DFA:
- $Q = \{A, B, C, D, E, F\}$
- $\Sigma = \{0, 1\}$
- $q_0 = A$
- $F = \{C, D\}$

**Transition Table:**
| State | on 0 | on 1 |
|---|---|---|
| **A** | B | C |
| **B** | A | D |
| **C** | E | F |
| **D** | E | F |
| **E** | E | F |
| **F** | F | E |

### Manual Trace of Partition Refinement:

#### Round 0 ($P_0$):
Split into Accepting and Non-Accepting states:
- $B_0 = \{C, D\}$ (Accepting)
- $B_1 = \{A, B, E, F\}$ (Non-Accepting)
$$P_0 = \{\{C, D\}, \{A, B, E, F\}\}$$

#### Round 1 ($P_1$):
- Examine $B_0 = \{C, D\}$:
  - For $C$: $\delta(C, 0) = E \in B_1$, $\delta(C, 1) = F \in B_1$. Signature: $(B_1, B_1)$.
  - For $D$: $\delta(D, 0) = E \in B_1$, $\delta(D, 1) = F \in B_1$. Signature: $(B_1, B_1)$.
  - Both states have identical signatures. $B_0$ does not split!

- Examine $B_1 = \{A, B, E, F\}$:
  - For $A$: $\delta(A, 0) = B \in B_1$, $\delta(A, 1) = C \in B_0$. Signature: $(B_1, B_0)$.
  - For $B$: $\delta(B, 0) = A \in B_1$, $\delta(B, 1) = D \in B_0$. Signature: $(B_1, B_0)$.
  - For $E$: $\delta(E, 0) = E \in B_1$, $\delta(E, 1) = F \in B_1$. Signature: $(B_1, B_1)$.
  - For $F$: $\delta(F, 0) = F \in B_1$, $\delta(F, 1) = E \in B_1$. Signature: $(B_1, B_1)$.
  - Notice that states $A$ and $B$ have signature $(B_1, B_0)$, while $E$ and $F$ have signature $(B_1, B_1)$.
  - Therefore, $B_1$ splits into $\{A, B\}$ and $\{E, F\}$!
$$P_1 = \{\{C, D\}, \{A, B\}, \{E, F\}\}$$

#### Round 2 ($P_2$):
Let the blocks be:
- $P_0 = \{C, D\}$
- $P_1 = \{A, B\}$
- $P_2 = \{E, F\}$

- Examine $\{A, B\}$:
  - $A \xrightarrow{0} B \in P_1$, $A \xrightarrow{1} C \in P_0 \implies (P_1, P_0)$.
  - $B \xrightarrow{0} A \in P_1$, $B \xrightarrow{1} D \in P_0 \implies (P_1, P_0)$.
  - Signatures match. $\{A, B\}$ stays intact.

- Examine $\{C, D\}$:
  - $C \xrightarrow{0} E \in P_2$, $C \xrightarrow{1} F \in P_2 \implies (P_2, P_2)$.
  - $D \xrightarrow{0} E \in P_2$, $D \xrightarrow{1} F \in P_2 \implies (P_2, P_2)$.
  - Signatures match. $\{C, D\}$ stays intact.

- Examine $\{E, F\}$:
  - $E \xrightarrow{0} E \in P_2$, $E \xrightarrow{1} F \in P_2 \implies (P_2, P_2)$.
  - $F \xrightarrow{0} F \in P_2$, $F \xrightarrow{1} E \in P_2 \implies (P_2, P_2)$.
  - Signatures match. $\{E, F\}$ stays intact.

No further block splitting is possible. **Stable Fixed Point Reached!**

### Resulting Minimized DFA:
- Minimized States: $\{[A, B], [C, D], [E, F]\}$ (or 4 states if distinguishing dead state behavior).
- State reduction: from 6 states down to minimal equivalence classes!

---

## 5. Architectural Diagram
```
+-----------------------------------------------------------+
|                   Presentation Layer                      |
|  - Cytoscape.js Graph Canvas (Circle, Physics Layouts)    |
|  - Step-by-Step Refinement Stepper (Play/Pause/Reset)     |
|  - Distinguishing Strings & Parallel Trace View           |
|  - Dual String Simulation & Product Automaton Proof UI    |
+-----------------------------------------------------------+
                             |
                             v REST API (JSON)
+-----------------------------------------------------------+
|                Flask Backend Controller                   |
|  - /api/dfa/validate       - /api/dfa/minimize            |
|  - /api/dfa/distinguish    - /api/dfa/simulate            |
|  - /api/dfa/verify-equivalence                            |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|               Theoretical Computation Engine              |
|  - automata.dfa: Validation & BFS Reachability            |
|  - automata.minimizer: Partition Refinement & Merging     |
|  - automata.distinguisher: BFS Distinguishing Strings     |
|  - automata.equivalence: Product Automaton Checker        |
+-----------------------------------------------------------+
```
