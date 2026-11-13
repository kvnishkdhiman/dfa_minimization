# DFA-Min: Interactive Automata Minimization & Equivalence Simulator

> **An Interactive Educational Simulation Laboratory for Deterministic Finite Automata (DFA) Minimization, Partition Refinement, and State Equivalence Verification.**

---

## 🌟 Overview
**DFA-Min** is a complete, interactive web-based simulator designed for students and educators in Automata Theory, Formal Languages, and Theory of Computation. It visually demonstrates how a Deterministic Finite Automaton is systematically minimized using the **Partition Refinement Algorithm** (Moore / Hopcroft), explains every partition split, generates shortest distinguishing strings, and formally verifies language equivalence using synchronous product automata.

---

## 🚀 Key Features

1. **Formal 5-Tuple DFA Specification:**
   - Define custom DFAs with $M = (Q, \Sigma, \delta, q_0, F)$.
   - Dynamic, auto-adjusting transition matrix editor.
   - Comprehensive validation (determinism, completeness, alphabet coverage, valid initial/accepting states).
   - Built-in benchmarks: Hopcroft 6-State, Unreachable States, 8-State Redundant, Parity Checker (Irreducible), Substring '01'.

2. **Graph Reachability Analysis:**
   - Automatic BFS graph traversal from initial state $q_0$.
   - Visual alerts and dimmed highlighting for unreachable states before minimization.

3. **Step-by-Step Partition Refinement Stepper:**
   - Interactive playback controls: **Next Step**, **Previous Step**, **Play (Auto-step with speed slider)**, **Pause**, **Reset**, **Jump to End**.
   - Dynamic color-coding of states matching partition blocks on Cytoscape.js canvas.
   - Educational split explanation box detailing which symbol and destination partition triggered each division.

4. **Shortest Distinguishing String Generator (Novelty Feature):**
   - Finds the minimal-length string $w \in \Sigma^*$ that proves why two states $p$ and $q$ are not equivalent ($\delta^*(p, w) \in F \iff \delta^*(q, w) \notin F$).
   - Step-by-step parallel path trace comparison.
   - Full Myhill-Nerode pairwise distinguishability matrix.

5. **Dual Automata String Simulation (Level 1 Testing):**
   - Test any input string simultaneously on both the Original and Minimized DFAs.
   - Live animated path highlighting across both Cytoscape.js diagrams.
   - Acceptance result consistency check.

6. **Formal Language Equivalence Verification (Level 2 Proof):**
   - Synchronous product automaton state space exploration.
   - Mathematical proof that $L(M_1) \equiv L(M_2)$ by verifying $L(M_1) \triangle L(M_2) = \emptyset$.
   - Counterexample generator if non-equivalent; formal cryptographic certificate badge if equivalent.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.14+, Flask (RESTful API), Pytest (Test Suite)
- **Frontend:** Modern Vanilla JavaScript (ES6+), HTML5, CSS3 (Modern Slate / Cyber-Academic Dark Theme)
- **Graph Visualization:** Cytoscape.js (Bundled locally + CDN fallback)
- **Architecture:** Three-Layer Modular Architecture (Presentation, Computation, Data Model)

---

## 📦 Quick Start Guide

### 1. Requirements
Ensure Python 3.9+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Simulator
```bash
python run.py
```
Or directly with Flask:
```bash
python app.py
```
The application will launch and open automatically at:
**`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests
Run the complete Pytest test suite:
```powershell
$env:PYTHONPATH="."
python -m pytest tests/ -v
```

---

## 👥 Five-Member Team Division
See [`docs/TEAM_ROLES.md`](file:///C:/Users/Ananya/OneDrive/Desktop/projects/Automata%20Project/docs/TEAM_ROLES.md) for full task details:
- **Member 1:** DFA Input, Validation & Matrix Generation
- **Member 2:** Reachability Analysis & Partition Refinement Algorithm
- **Member 3:** Interactive Cytoscape.js Graph Visualization & Merging
- **Member 4:** Verification, Distinguishing Strings & Equivalence Proof
- **Member 5:** UI/UX, Frontend Integration & Lab Documentation

---

## 📑 Lab Evaluation Milestones
- **Milestone 1 (Design - 5 Marks):** See [`docs/M1_DESIGN_DOCUMENT.md`](file:///C:/Users/Ananya/OneDrive/Desktop/projects/Automata%20Project/docs/M1_DESIGN_DOCUMENT.md)
- **Milestone 2 (Implementation & Demo - 9 Marks):** See [`docs/M2_IMPLEMENTATION.md`](file:///C:/Users/Ananya/OneDrive/Desktop/projects/Automata%20Project/docs/M2_IMPLEMENTATION.md)
