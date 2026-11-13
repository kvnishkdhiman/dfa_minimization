"""
Unit tests for the Distinguishing String Finder.
"""

import pytest
from automata.dfa import DFA
from automata.distinguisher import DistinguishingStringFinder


def test_distinguishing_epsilon():
    """State A is non-accepting and C is accepting -> distinguished by empty string epsilon."""
    dfa = DFA(
        states=["A", "B", "C"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "C"},
            "C": {"0": "C", "1": "C"},
        },
        initial_state="A",
        accepting_states=["C"],
    )
    finder = DistinguishingStringFinder(dfa)
    res = finder.find_distinguishing_string("A", "C")
    assert res["distinguishable"] is True
    assert res["equivalent"] is False
    assert res["string"] == ""
    assert res["length"] == 0


def test_distinguishing_non_trivial_string():
    """
    States A and B:
    A on 0 goes to A, on 1 goes to C (accepting).
    B on 0 goes to B, on 1 goes to B (non-accepting).
    String '1' distinguishes them!
    """
    dfa = DFA(
        states=["A", "B", "C"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "A", "1": "C"},
            "B": {"0": "B", "1": "B"},
            "C": {"0": "C", "1": "C"},
        },
        initial_state="A",
        accepting_states=["C"],
    )
    finder = DistinguishingStringFinder(dfa)
    res = finder.find_distinguishing_string("A", "B")
    assert res["distinguishable"] is True
    assert res["string"] == "1"
    assert res["accepted_p"] is True
    assert res["accepted_q"] is False


def test_equivalent_states():
    """Identical behavior states."""
    dfa = DFA(
        states=["A", "B", "C"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "C"},
            "C": {"0": "C", "1": "C"},
        },
        initial_state="A",
        accepting_states=["C"],
    )
    finder = DistinguishingStringFinder(dfa)
    res = finder.find_distinguishing_string("A", "B")
    assert res["distinguishable"] is False
    assert res["equivalent"] is True
    assert res["string"] is None


def test_all_pairs_table():
    dfa = DFA(
        states=["A", "B"],
        alphabet=["0"],
        transitions={
            "A": {"0": "B"},
            "B": {"0": "A"},
        },
        initial_state="A",
        accepting_states=["B"],
    )
    finder = DistinguishingStringFinder(dfa)
    table_res = finder.compute_all_pairs_table()
    assert "A" in table_res["table"]
    assert "B" in table_res["table"]["A"]
    assert table_res["table"]["A"]["B"]["distinguishable"] is True
