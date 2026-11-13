"""
API endpoint tests for Flask server routes.
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"DFA-Min" in res.data


def test_presets_route(client):
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "textbook_6_state" in data["presets"]


def test_validate_api(client):
    payload = {
        "states": ["A", "B"],
        "alphabet": ["0", "1"],
        "transitions": {
            "A": {"0": "B", "1": "A"},
            "B": {"0": "A", "1": "B"},
        },
        "initial_state": "A",
        "accepting_states": ["B"],
    }
    res = client.post("/api/dfa/validate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["is_valid"] is True
    assert len(data["elements"]) > 0


def test_minimize_api(client):
    payload = {
        "states": ["A", "B", "C"],
        "alphabet": ["0"],
        "transitions": {
            "A": {"0": "B"},
            "B": {"0": "C"},
            "C": {"0": "C"},
        },
        "initial_state": "A",
        "accepting_states": ["C"],
    }
    res = client.post("/api/dfa/minimize", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total_steps"] >= 1


def test_distinguish_api(client):
    payload = {
        "dfa": {
            "states": ["A", "B"],
            "alphabet": ["0"],
            "transitions": {
                "A": {"0": "A"},
                "B": {"0": "B"},
            },
            "initial_state": "A",
            "accepting_states": ["B"],
        },
        "state_p": "A",
        "state_q": "B",
    }
    res = client.post("/api/dfa/distinguish", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["distinguishable"] is True


def test_simulate_api(client):
    dfa = {
        "states": ["A", "B"],
        "alphabet": ["0", "1"],
        "transitions": {
            "A": {"0": "B", "1": "A"},
            "B": {"0": "B", "1": "A"},
        },
        "initial_state": "A",
        "accepting_states": ["B"],
    }
    payload = {
        "original_dfa": dfa,
        "minimized_dfa": dfa,
        "input_string": "010",
    }
    res = client.post("/api/dfa/simulate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["match"] is True


def test_verify_equivalence_api(client):
    dfa = {
        "states": ["A", "B"],
        "alphabet": ["0"],
        "transitions": {
            "A": {"0": "B"},
            "B": {"0": "A"},
        },
        "initial_state": "A",
        "accepting_states": ["B"],
    }
    payload = {
        "dfa1": dfa,
        "dfa2": dfa,
    }
    res = client.post("/api/dfa/verify-equivalence", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["verification"]["is_equivalent"] is True
