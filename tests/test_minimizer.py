"""
Unit tests for the Partition Refinement DFA Minimization algorithm.
"""

import pytest
from automata.dfa import DFA
from automata.minimizer import DFAMinimizer


def test_textbook_minimization():
    """
    Standard textbook 6-state DFA minimization:
    States: A, B, C, D, E, F
    Alphabet: 0, 1
    Start: A
    Accepting: C, D
    Transitions:
      A: 0->B, 1->C
      B: 0->A, 1->D
      C: 0->E, 1->F
      D: 0->E, 1->F
      E: 0->E, 1->F
      F: 0->F, 1->E
    """
    dfa = DFA(
        states=["A", "B", "C", "D", "E", "F"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "D"},
            "C": {"0": "E", "1": "F"},
            "D": {"0": "E", "1": "F"},
            "E": {"0": "E", "1": "F"},
            "F": {"0": "F", "1": "E"},
        },
        initial_state="A",
        accepting_states=["C", "D"],
    )

    minimizer = DFAMinimizer(dfa)
    result = minimizer.run_all()

    assert result["success"] is True
    assert result["total_steps"] >= 2
    # Check that A and B are in the same equivalence class
    eq_classes = result["equivalence_classes"]
    
    # Find block containing A
    a_block = next(b for b in eq_classes if "A" in b)
    assert "B" in a_block
    
    # Find block containing C
    c_block = next(b for b in eq_classes if "C" in b)
    assert "D" in c_block

    # Minimized DFA is created
    assert minimizer.minimized_dfa is not None
    assert minimizer.minimized_dfa.initial_state is not None
    assert len(minimizer.minimized_dfa.accepting_states) > 0


def test_already_minimal_dfa():
    """DFA recognizing strings ending with 1 over {0, 1} with 2 states: S0, S1."""
    dfa = DFA(
        states=["S0", "S1"],
        alphabet=["0", "1"],
        transitions={
            "S0": {"0": "S0", "1": "S1"},
            "S1": {"0": "S0", "1": "S1"},
        },
        initial_state="S0",
        accepting_states=["S1"],
    )
    minimizer = DFAMinimizer(dfa)
    result = minimizer.run_all()
    # Cannot be reduced further
    assert result["minimized_states_count"] == 2
    assert len(result["equivalent_pairs"]) == 0


def test_all_accepting_states():
    """All states are accepting and identical."""
    dfa = DFA(
        states=["q0", "q1"],
        alphabet=["0", "1"],
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q0", "1": "q1"},
        },
        initial_state="q0",
        accepting_states=["q0", "q1"],
    )
    minimizer = DFAMinimizer(dfa)
    result = minimizer.run_all()
    assert result["minimized_states_count"] == 1


def test_unreachable_state_removal():
    """DFA with an unreachable state Z."""
    dfa = DFA(
        states=["A", "B", "Z"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "B", "1": "A"},
            "B": {"0": "A", "1": "B"},
            "Z": {"0": "A", "1": "B"},
        },
        initial_state="A",
        accepting_states=["B"],
    )
    minimizer = DFAMinimizer(dfa)
    result = minimizer.run_all()
    assert "Z" in result["unreachable_states"]
    assert result["reachable_states_count"] == 2
