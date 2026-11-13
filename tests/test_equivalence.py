"""
Unit tests for the Language Equivalence Checker using Product Automaton verification.
"""

import pytest
from automata.dfa import DFA
from automata.minimizer import DFAMinimizer
from automata.equivalence import LanguageEquivalenceChecker


def test_minimized_equivalence():
    """Verify that original DFA and its minimized DFA are strictly language equivalent."""
    original = DFA(
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

    minimizer = DFAMinimizer(original)
    minimizer.run_all()
    minimized = minimizer.minimized_dfa

    checker = LanguageEquivalenceChecker(original.filter_unreachable(), minimized)
    result = checker.verify()

    assert result["is_equivalent"] is True
    assert result["counterexample"] is None
    assert result["proof_certificate"]["status"] == "VERIFIED_EQUIVALENT"


def test_non_equivalent_dfas():
    """Two DFAs recognizing different languages."""
    # DFA1 accepts strings with at least one '1'
    dfa1 = DFA(
        states=["S0", "S1"],
        alphabet=["0", "1"],
        transitions={
            "S0": {"0": "S0", "1": "S1"},
            "S1": {"0": "S1", "1": "S1"},
        },
        initial_state="S0",
        accepting_states=["S1"],
    )
    # DFA2 accepts strings with at least one '0'
    dfa2 = DFA(
        states=["T0", "T1"],
        alphabet=["0", "1"],
        transitions={
            "T0": {"0": "T1", "1": "T0"},
            "T1": {"0": "T1", "1": "T1"},
        },
        initial_state="T0",
        accepting_states=["T1"],
    )

    checker = LanguageEquivalenceChecker(dfa1, dfa2)
    result = checker.verify()

    assert result["is_equivalent"] is False
    assert result["counterexample"] is not None
    assert result["proof_certificate"]["status"] in ["FAILED", "DISPROVED"]
