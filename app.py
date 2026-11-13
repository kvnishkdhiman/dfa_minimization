"""
DFA-Min Flask Application Server.
Provides RESTful APIs for DFA validation, step-by-step partition refinement,
distinguishing string generation, string simulation, and formal language equivalence verification.
"""

import sys
import os
from typing import Dict, Any

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, jsonify
from automata.dfa import DFA
from automata.minimizer import DFAMinimizer
from automata.distinguisher import DistinguishingStringFinder
from automata.equivalence import LanguageEquivalenceChecker

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# Built-in educational preset benchmarks
PRESETS: Dict[str, Dict[str, Any]] = {
    "textbook_6_state": {
        "name": "Textbook 6-State DFA (Hopcroft Example)",
        "description": "Standard 6-state DFA with states A, B equivalent and C, D equivalent.",
        "dfa": {
            "states": ["A", "B", "C", "D", "E", "F"],
            "alphabet": ["0", "1"],
            "transitions": {
                "A": {"0": "B", "1": "C"},
                "B": {"0": "A", "1": "D"},
                "C": {"0": "E", "1": "F"},
                "D": {"0": "E", "1": "F"},
                "E": {"0": "E", "1": "F"},
                "F": {"0": "F", "1": "E"},
            },
            "initial_state": "A",
            "accepting_states": ["C", "D"],
        },
    },
    "unreachable_states": {
        "name": "DFA with Unreachable States",
        "description": "States U1 and U2 cannot be reached from initial state q0 and should be pruned before refinement.",
        "dfa": {
            "states": ["q0", "q1", "q2", "U1", "U2"],
            "alphabet": ["a", "b"],
            "transitions": {
                "q0": {"a": "q1", "b": "q0"},
                "q1": {"a": "q2", "b": "q1"},
                "q2": {"a": "q2", "b": "q2"},
                "U1": {"a": "q1", "b": "U2"},
                "U2": {"a": "U1", "b": "q0"},
            },
            "initial_state": "q0",
            "accepting_states": ["q2", "U2"],
        },
    },
    "multiple_redundancies": {
        "name": "Complex 8-State DFA with Multiple Merges",
        "description": "An 8-state automaton with cascaded state equivalence classes.",
        "dfa": {
            "states": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "alphabet": ["0", "1"],
            "transitions": {
                "A": {"0": "B", "1": "F"},
                "B": {"0": "G", "1": "C"},
                "C": {"0": "A", "1": "C"},
                "D": {"0": "C", "1": "G"},
                "E": {"0": "H", "1": "F"},
                "F": {"0": "C", "1": "G"},
                "G": {"0": "G", "1": "E"},
                "H": {"0": "G", "1": "C"},
            },
            "initial_state": "A",
            "accepting_states": ["C"],
        },
    },
    "even_zeros_even_ones": {
        "name": "Even 0s and Even 1s (Already Minimal)",
        "description": "Classical parity checker recognizing strings with even count of 0s and 1s. Irreducible.",
        "dfa": {
            "states": ["qEE", "qOE", "qEO", "qOO"],
            "alphabet": ["0", "1"],
            "transitions": {
                "qEE": {"0": "qOE", "1": "qEO"},
                "qOE": {"0": "qEE", "1": "qOO"},
                "qEO": {"0": "qOO", "1": "qEE"},
                "qOO": {"0": "qEO", "1": "qOE"},
            },
            "initial_state": "qEE",
            "accepting_states": ["qEE"],
        },
    },
    "contains_01": {
        "name": "Contains Substring '01'",
        "description": "3-state DFA that accepts any binary string containing '01'.",
        "dfa": {
            "states": ["q0", "q1", "q2"],
            "alphabet": ["0", "1"],
            "transitions": {
                "q0": {"0": "q1", "1": "q0"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            "initial_state": "q0",
            "accepting_states": ["q2"],
        },
    },
}


@app.route("/")
def index():
    """Renders the main DFA-Min simulator user interface."""
    return render_template("index.html")


@app.route("/api/presets", methods=["GET"])
def get_presets():
    """Returns available benchmark preset DFAs."""
    return jsonify({"success": True, "presets": PRESETS})


@app.route("/api/dfa/validate", methods=["POST"])
def validate_dfa():
    """
    Validates user DFA input, identifies reachability, and returns graph elements.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON payload."}), 400

    try:
        dfa = DFA.from_dict(data)
        is_valid, err_msg = dfa.validate()
        if not is_valid:
            return jsonify({"success": False, "error": err_msg}), 400

        reachable, unreachable = dfa.get_reachable_states()
        elements = dfa.to_cytoscape_elements(unreachable_states=unreachable)

        return jsonify({
            "success": True,
            "is_valid": True,
            "reachable_states": reachable,
            "unreachable_states": unreachable,
            "elements": elements,
            "dfa": dfa.to_dict(),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/dfa/minimize", methods=["POST"])
def minimize_dfa():
    """
    Runs complete Partition Refinement minimization on the DFA.
    Returns step-by-step history, split explanations, equivalence classes, and minimized DFA.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON input."}), 400

    try:
        dfa = DFA.from_dict(data)
        is_valid, err_msg = dfa.validate()
        if not is_valid:
            return jsonify({"success": False, "error": err_msg}), 400

        minimizer = DFAMinimizer(dfa)
        result = minimizer.run_all()

        # Build Cytoscape elements with partition coloring
        final_block_map: Dict[str, int] = {}
        for block_idx, block in enumerate(result["equivalence_classes"]):
            for s in block:
                final_block_map[s] = block_idx

        original_elements = dfa.to_cytoscape_elements(
            partition_map=final_block_map,
            unreachable_states=result["unreachable_states"]
        )

        result["original_elements"] = original_elements
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/dfa/distinguish", methods=["POST"])
def distinguish_states():
    """
    Finds the shortest distinguishing string between two selected states.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "dfa" not in data or "state_p" not in data or "state_q" not in data:
        return jsonify({"success": False, "error": "Must provide dfa, state_p, and state_q."}), 400

    try:
        dfa = DFA.from_dict(data["dfa"])
        dfa.assert_valid()
        finder = DistinguishingStringFinder(dfa)
        result = finder.find_distinguishing_string(data["state_p"], data["state_q"])
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/dfa/distinguish-all", methods=["POST"])
def distinguish_all_pairs():
    """
    Computes pairwise distinguishability for all state pairs.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "dfa" not in data:
        return jsonify({"success": False, "error": "Must provide dfa."}), 400

    try:
        dfa = DFA.from_dict(data["dfa"])
        dfa.assert_valid()
        finder = DistinguishingStringFinder(dfa)
        table = finder.compute_all_pairs_table()
        return jsonify({"success": True, "table": table})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/dfa/simulate", methods=["POST"])
def simulate_string():
    """
    Simulates input string on both original DFA and minimized DFA.
    Shows paths, states visited, acceptance, and compares equivalence.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "original_dfa" not in data or "minimized_dfa" not in data:
        return jsonify({"success": False, "error": "Missing original_dfa or minimized_dfa."}), 400

    test_string = str(data.get("input_string", "")).strip()

    try:
        orig_dfa = DFA.from_dict(data["original_dfa"])
        min_dfa = DFA.from_dict(data["minimized_dfa"])

        orig_result = orig_dfa.simulate(test_string)
        min_result = min_dfa.simulate(test_string)

        match = (orig_result.get("accepted") == min_result.get("accepted"))

        return jsonify({
            "success": True,
            "test_string": test_string,
            "original_result": orig_result,
            "minimized_result": min_result,
            "match": match,
            "status": "ACCEPTED" if orig_result.get("accepted") else "REJECTED",
            "is_consistent": match,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/dfa/verify-equivalence", methods=["POST"])
def verify_equivalence():
    """
    Performs formal language-equivalence verification using product-automaton state exploration.
    Mathematically proves L(M1) == L(M2) or produces a counterexample.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "dfa1" not in data or "dfa2" not in data:
        return jsonify({"success": False, "error": "Must provide dfa1 and dfa2."}), 400

    try:
        dfa1 = DFA.from_dict(data["dfa1"])
        dfa2 = DFA.from_dict(data["dfa2"])

        checker = LanguageEquivalenceChecker(dfa1.filter_unreachable(), dfa2.filter_unreachable())
        result = checker.verify()
        return jsonify({"success": True, "verification": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting DFA-Min Simulator on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
