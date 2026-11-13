"""
Unit tests for DFA representation, validation, reachability, and simulation.
"""

import pytest
from automata.dfa import DFA, DFAValidationError


def create_sample_dfa():
    """Returns the 6-state textbook DFA."""
    return DFA(
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


def test_valid_dfa():
    dfa = create_sample_dfa()
    is_valid, err = dfa.validate()
    assert is_valid is True
    assert err is None


def test_empty_states():
    dfa = DFA(
        states=[],
        alphabet=["0", "1"],
        transitions={},
        initial_state="A",
        accepting_states=[],
    )
    is_valid, err = dfa.validate()
    assert is_valid is False
    assert "cannot be empty" in err


def test_invalid_initial_state():
    dfa = DFA(
        states=["A", "B"],
        alphabet=["0"],
        transitions={"A": {"0": "B"}, "B": {"0": "A"}},
        initial_state="Z",
        accepting_states=["B"],
    )
    is_valid, err = dfa.validate()
    assert is_valid is False
    assert "Initial state 'Z' does not belong" in err


def test_invalid_accepting_state():
    dfa = DFA(
        states=["A", "B"],
        alphabet=["0"],
        transitions={"A": {"0": "B"}, "B": {"0": "A"}},
        initial_state="A",
        accepting_states=["Z"],
    )
    is_valid, err = dfa.validate()
    assert is_valid is False
    assert "Accepting states" in err


def test_missing_transition():
    dfa = DFA(
        states=["A", "B"],
        alphabet=["0", "1"],
        transitions={"A": {"0": "B"}, "B": {"0": "A", "1": "B"}},
        initial_state="A",
        accepting_states=["B"],
    )
    is_valid, err = dfa.validate()
    assert is_valid is False
    assert "no transition defined for symbol '1'" in err


def test_reachability():
    # A -> B -> A. State C and D are unreachable.
    dfa = DFA(
        states=["A", "B", "C", "D"],
        alphabet=["0", "1"],
        transitions={
            "A": {"0": "B", "1": "A"},
            "B": {"0": "A", "1": "B"},
            "C": {"0": "C", "1": "D"},
            "D": {"0": "C", "1": "D"},
        },
        initial_state="A",
        accepting_states=["B", "C"],
    )
    reachable, unreachable = dfa.get_reachable_states()
    assert reachable == ["A", "B"]
    assert unreachable == ["C", "D"]

    filtered = dfa.filter_unreachable()
    assert filtered.states == ["A", "B"]
    assert filtered.accepting_states == ["B"]


def test_simulation():
    dfa = create_sample_dfa()
    # '1' from A -> C (accepting)
    res1 = dfa.simulate("1")
    assert res1["valid"] is True
    assert res1["accepted"] is True
    assert res1["final_state"] == "C"

    # '01' from A -> B -> D (accepting)
    res2 = dfa.simulate("01")
    assert res2["valid"] is True
    assert res2["accepted"] is True
    assert res2["final_state"] == "D"

    # '000' from A -> B -> A -> B (non-accepting)
    res3 = dfa.simulate("000")
    assert res3["valid"] is True
    assert res3["accepted"] is False

    # Invalid symbol '2'
    res4 = dfa.simulate("012")
    assert res4["valid"] is False
    assert "does not belong to alphabet" in res4["error"]
