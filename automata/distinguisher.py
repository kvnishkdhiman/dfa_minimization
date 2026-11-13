"""
Distinguishing String Generator Module.
Finds the shortest distinguishing string between any two states using BFS on state pairs,
and verifies why non-equivalent states cannot be merged.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from collections import deque
from .dfa import DFA


class DistinguishingStringFinder:
    """
    Computes shortest distinguishing strings between states in a DFA.
    For states p and q, a string w distinguishes them if:
    delta*(p, w) in F and delta*(q, w) not in F (or vice-versa).
    """

    def __init__(self, dfa: DFA):
        self.dfa = dfa

    def find_distinguishing_string(self, state_p: str, state_q: str) -> Dict[str, Any]:
        """
        Finds the shortest distinguishing string between state_p and state_q.
        Returns:
            Dictionary containing:
            - distinguishable: bool
            - string: str (shortest distinguishing string, or empty string, or None if equivalent)
            - length: int
            - trace_p: list of states visited from state_p
            - trace_q: list of states visited from state_q
            - final_p: ending state of p
            - final_q: ending state of q
            - accepted_p: bool
            - accepted_q: bool
            - explanation: educational text
        """
        self.dfa.assert_valid()
        p = str(state_p).strip()
        q = str(state_q).strip()

        if p not in self.dfa.states:
            return {"error": f"State '{p}' is not in the DFA states."}
        if q not in self.dfa.states:
            return {"error": f"State '{q}' is not in the DFA states."}

        # Case 1: Same state is trivially equivalent
        if p == q:
            return {
                "distinguishable": False,
                "equivalent": True,
                "string": None,
                "length": 0,
                "explanation": f"State '{p}' and state '{q}' are identical states, hence trivially equivalent.",
            }

        accepting_set = set(self.dfa.accepting_states)
        p_acc = p in accepting_set
        q_acc = q in accepting_set

        # Case 2: One is accepting and one is non-accepting -> distinguished by epsilon (empty string)
        if p_acc != q_acc:
            p_status = "Accepting" if p_acc else "Rejecting"
            q_status = "Accepting" if q_acc else "Rejecting"
            return {
                "distinguishable": True,
                "equivalent": False,
                "string": "",
                "display_string": "ε (empty string)",
                "length": 0,
                "trace_p": [p],
                "trace_q": [q],
                "final_p": p,
                "final_q": q,
                "accepted_p": p_acc,
                "accepted_q": q_acc,
                "explanation": (
                    f"Distinguished by the empty string ε (length 0). "
                    f"State '{p}' is {p_status} while state '{q}' is {q_status}."
                ),
            }

        # Case 3: BFS on state pairs to find shortest distinguishing string
        # Queue item: (curr_p, curr_q, string_so_far)
        queue: deque = deque([(p, q, "")])
        visited: Set[Tuple[str, str]] = set()
        visited.add((p, q))
        visited.add((q, p))

        alphabet = sorted(self.dfa.alphabet)

        while queue:
            curr_p, curr_q, s_str = queue.popleft()

            for sym in alphabet:
                next_p = self.dfa.transitions[curr_p][sym]
                next_q = self.dfa.transitions[curr_q][sym]
                cand_str = s_str + sym

                next_p_acc = next_p in accepting_set
                next_q_acc = next_q in accepting_set

                # Check if this input differentiates them
                if next_p_acc != next_q_acc:
                    # Found shortest distinguishing string!
                    dist_str = cand_str
                    # Compute full step traces
                    trace_p = self._compute_trace(p, dist_str)
                    trace_q = self._compute_trace(q, dist_str)

                    p_end_status = "Accepting" if next_p_acc else "Rejecting"
                    q_end_status = "Accepting" if next_q_acc else "Rejecting"

                    explanation = (
                        f"Distinguished by string \"{dist_str}\" (length {len(dist_str)}): "
                        f"δ*({p}, \"{dist_str}\") = {next_p} ({p_end_status}), whereas "
                        f"δ*({q}, \"{dist_str}\") = {next_q} ({q_end_status}). "
                        f"Since one reaches an accepting state and the other does not, {p} and {q} cannot be merged."
                    )

                    return {
                        "distinguishable": True,
                        "equivalent": False,
                        "string": dist_str,
                        "display_string": dist_str,
                        "length": len(dist_str),
                        "trace_p": trace_p,
                        "trace_q": trace_q,
                        "final_p": next_p,
                        "final_q": next_q,
                        "accepted_p": next_p_acc,
                        "accepted_q": next_q_acc,
                        "explanation": explanation,
                    }

                pair = (next_p, next_q)
                if pair not in visited:
                    visited.add((next_p, next_q))
                    visited.add((next_q, next_p))
                    queue.append((next_p, next_q, cand_str))

        # If BFS completes without finding a distinguishing string, they are equivalent!
        return {
            "distinguishable": False,
            "equivalent": True,
            "string": None,
            "display_string": None,
            "length": 0,
            "explanation": (
                f"No input string can distinguish states '{p}' and '{q}'. "
                f"For all possible inputs w ∈ Σ*, δ*({p}, w) and δ*({q}, w) have identical acceptance behavior. "
                f"Therefore, {p} ≡ {q} and they are merged in the minimized DFA."
            ),
        }

    def _compute_trace(self, start_state: str, input_str: str) -> List[Dict[str, Any]]:
        """Computes step-by-step trace from start_state along input_str."""
        trace = [{"state": start_state, "symbol": None}]
        curr = start_state
        for sym in input_str:
            curr = self.dfa.transitions[curr][sym]
            trace.append({"state": curr, "symbol": sym})
        return trace

    def compute_all_pairs_table(self) -> Dict[str, Any]:
        """
        Computes pairwise distinguishability for all state pairs.
        Returns matrix data suitable for an interactive Myhill-Nerode / Table-Filling view.
        """
        states = sorted(self.dfa.states)
        table: Dict[str, Dict[str, Any]] = {}

        for i, s1 in enumerate(states):
            table[s1] = {}
            for j, s2 in enumerate(states):
                if j > i:  # Upper triangle
                    res = self.find_distinguishing_string(s1, s2)
                    table[s1][s2] = {
                        "distinguishable": res["distinguishable"],
                        "string": res.get("display_string", "-"),
                        "explanation": res["explanation"],
                    }

        return {
            "states": states,
            "table": table,
        }
