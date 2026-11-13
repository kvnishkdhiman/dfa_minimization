"""
Formal Language Equivalence Verification Module.
Implements the Product-Automaton state space exploration algorithm
to mathematically prove or disprove L(M1) == L(M2) with counterexample generation.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from collections import deque
from .dfa import DFA


class LanguageEquivalenceChecker:
    """
    Formally verifies whether two DFAs recognize the exact same regular language.
    Constructs and traverses the synchronous product automaton (M1 x M2)
    to check the emptiness of the symmetric difference L(M1) △ L(M2).
    """

    def __init__(self, dfa1: DFA, dfa2: DFA):
        self.dfa1 = dfa1
        self.dfa2 = dfa2

    def verify(self) -> Dict[str, Any]:
        """
        Executes formal equivalence verification.
        Returns:
            Dictionary containing:
            - is_equivalent: bool
            - states_explored: int
            - max_product_states: int
            - counterexample: Optional[str]
            - counterexample_m1_result: Optional[bool]
            - counterexample_m2_result: Optional[bool]
            - product_states_visited: List[Tuple[str, str]]
            - proof_certificate: Dict[str, Any]
            - explanation: str
        """
        self.dfa1.assert_valid()
        self.dfa2.assert_valid()

        # Alphabets must be identical
        s1_alpha = set(self.dfa1.alphabet)
        s2_alpha = set(self.dfa2.alphabet)
        if s1_alpha != s2_alpha:
            return {
                "is_equivalent": False,
                "error": f"Alphabets do not match: DFA1 has {sorted(list(s1_alpha))}, DFA2 has {sorted(list(s2_alpha))}.",
                "explanation": "DFAs with differing alphabets cannot recognize the same formal language.",
            }

        alphabet = sorted(self.dfa1.alphabet)
        f1 = set(self.dfa1.accepting_states)
        f2 = set(self.dfa2.accepting_states)

        start_pair = (self.dfa1.initial_state, self.dfa2.initial_state)
        max_possible_states = len(self.dfa1.states) * len(self.dfa2.states)

        # Check start pair immediately (epsilon string test)
        if (start_pair[0] in f1) != (start_pair[1] in f2):
            w = ""
            return {
                "is_equivalent": False,
                "states_explored": 1,
                "max_product_states": max_possible_states,
                "counterexample": w,
                "display_counterexample": "ε (empty string)",
                "counterexample_m1_result": start_pair[0] in f1,
                "counterexample_m2_result": start_pair[1] in f2,
                "proof_certificate": {
                    "method": "Product Automaton Symmetric Difference Emptiness",
                    "status": "FAILED",
                    "distinguishing_string": w,
                },
                "explanation": (
                    "DFAs are NOT equivalent. The empty string ε is accepted by one DFA "
                    "and rejected by the other."
                ),
            }

        # BFS on product automaton states
        # Queue item: (state1, state2, string_path)
        queue: deque = deque([(start_pair[0], start_pair[1], "")])
        visited: Set[Tuple[str, str]] = {start_pair}
        visited_list: List[Tuple[str, str]] = [start_pair]

        while queue:
            p, q, path = queue.popleft()

            for sym in alphabet:
                next_p = self.dfa1.transitions[p][sym]
                next_q = self.dfa2.transitions[q][sym]
                next_path = path + sym

                # Check symmetric difference condition:
                # (next_p in F1 and next_q not in F2) or (next_p not in F1 and next_q in F2)
                p_in_f = next_p in f1
                q_in_f = next_q in f2

                if p_in_f != q_in_f:
                    # Counterexample found!
                    return {
                        "is_equivalent": False,
                        "states_explored": len(visited) + 1,
                        "max_product_states": max_possible_states,
                        "counterexample": next_path,
                        "display_counterexample": next_path,
                        "counterexample_m1_result": p_in_f,
                        "counterexample_m2_result": q_in_f,
                        "proof_certificate": {
                            "method": "Product Automaton Symmetric Difference Emptiness",
                            "status": "DISPROVED",
                            "counterexample": next_path,
                            "explored_states_count": len(visited) + 1,
                        },
                        "explanation": (
                            f"DFAs are NOT equivalent! Counterexample string '{next_path}' leads to "
                            f"state {next_p} ({'Accepting' if p_in_f else 'Rejecting'}) in DFA 1 and "
                            f"state {next_q} ({'Accepting' if q_in_f else 'Rejecting'}) in DFA 2."
                        ),
                    }

                nxt_pair = (next_p, next_q)
                if nxt_pair not in visited:
                    visited.add(nxt_pair)
                    visited_list.append(nxt_pair)
                    queue.append((next_p, next_q, next_path))

        # If the entire reachable product state space has been explored with no mismatch:
        return {
            "is_equivalent": True,
            "states_explored": len(visited),
            "max_product_states": max_possible_states,
            "counterexample": None,
            "display_counterexample": None,
            "product_states_visited": [f"({p}, {q})" for p, q in visited_list],
            "proof_certificate": {
                "method": "Product Automaton Symmetric Difference Emptiness [Hopcroft & Ullman]",
                "status": "VERIFIED_EQUIVALENT",
                "statement": "L(M1) == L(M2)",
                "reachable_product_states": len(visited),
                "theoretical_upper_bound": max_possible_states,
                "symmetric_difference_empty": True,
            },
            "explanation": (
                f"Formally Verified: L(Original DFA) ≡ L(Minimized DFA). "
                f"Traversed all {len(visited)} reachable states in the product automaton Q1 × Q2 "
                f"(out of {max_possible_states} theoretical pairs). No state in "
                f"(F1 × (Q2 \\ F2)) ∪ ((Q1 \\ F1) × F2) was reached. "
                "The symmetric difference language is strictly empty."
            ),
        }
