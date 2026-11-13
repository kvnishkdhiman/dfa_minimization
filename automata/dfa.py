"""
DFA Definition, Validation, Reachability Analysis, and Simulation Module.
Formally represents M = (Q, Sigma, delta, q0, F).
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque


class DFAValidationError(Exception):
    """Custom exception raised when DFA validation fails."""
    pass


class DFA:
    """
    Deterministic Finite Automaton (DFA).
    
    Attributes:
        states: List of state names (Q)
        alphabet: List of alphabet symbols (Sigma)
        transitions: Dict mapping state -> (dict mapping symbol -> next_state) (delta)
        initial_state: Name of initial state (q0)
        accepting_states: List of accepting/final state names (F)
    """

    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[str, Dict[str, str]],
        initial_state: str,
        accepting_states: List[str],
    ):
        # Normalize inputs: strip whitespace and keep deterministic ordering
        self.states: List[str] = [str(s).strip() for s in states]
        self.alphabet: List[str] = [str(a).strip() for a in alphabet]
        self.initial_state: str = str(initial_state).strip()
        self.accepting_states: List[str] = [str(s).strip() for s in accepting_states]
        
        # Clean transitions map
        self.transitions: Dict[str, Dict[str, str]] = {}
        for s, sym_map in transitions.items():
            s_clean = str(s).strip()
            self.transitions[s_clean] = {}
            for sym, tgt in sym_map.items():
                self.transitions[s_clean][str(sym).strip()] = str(tgt).strip()

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validates the DFA against standard formal language theory requirements:
        1. States set Q cannot be empty and state names must be unique.
        2. Alphabet Sigma cannot be empty and symbols must be unique.
        3. Initial state q0 must be in Q.
        4. Accepting states F must be a subset of Q.
        5. Completeness & Determinism: For every state q in Q and symbol a in Sigma,
           delta(q, a) must be defined and lead to a state in Q.
        """
        # 1. State validation
        if not self.states:
            return False, "State set Q cannot be empty."
        if len(self.states) != len(set(self.states)):
            return False, "Duplicate state names detected in Q."

        # 2. Alphabet validation
        if not self.alphabet:
            return False, "Alphabet Sigma cannot be empty."
        if len(self.alphabet) != len(set(self.alphabet)):
            return False, "Duplicate symbols detected in alphabet Sigma."

        states_set = set(self.states)

        # 3. Initial state validation
        if not self.initial_state:
            return False, "Initial state q0 must be specified."
        if self.initial_state not in states_set:
            return False, f"Initial state '{self.initial_state}' does not belong to state set Q."

        # 4. Accepting states validation
        accepting_set = set(self.accepting_states)
        invalid_accept = accepting_set - states_set
        if invalid_accept:
            return False, f"Accepting states {sorted(list(invalid_accept))} do not belong to state set Q."

        # 5. Transition function validation
        for state in self.states:
            if state not in self.transitions:
                return False, f"Missing transitions for state '{state}'."
            state_trans = self.transitions[state]
            for sym in self.alphabet:
                if sym not in state_trans:
                    return False, f"State '{state}' has no transition defined for symbol '{sym}'."
                target = state_trans[sym]
                if target not in states_set:
                    return False, f"Transition delta('{state}', '{sym}') -> '{target}' points to unknown state."

        return True, None

    def assert_valid(self) -> None:
        """Raises DFAValidationError if invalid."""
        is_valid, msg = self.validate()
        if not is_valid:
            raise DFAValidationError(msg)

    def get_reachable_states(self) -> Tuple[List[str], List[str]]:
        """
        Finds all reachable states from initial_state using Breadth-First Search (BFS).
        Returns:
            reachable: sorted list of reachable state names
            unreachable: sorted list of unreachable state names
        """
        self.assert_valid()
        visited: Set[str] = set()
        queue: deque = deque([self.initial_state])
        visited.add(self.initial_state)

        while queue:
            curr = queue.popleft()
            for sym in self.alphabet:
                nxt = self.transitions[curr][sym]
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        # Preserve state order from original states list
        reachable = [s for s in self.states if s in visited]
        unreachable = [s for s in self.states if s not in visited]
        return reachable, unreachable

    def filter_unreachable(self) -> "DFA":
        """
        Constructs a new DFA containing only reachable states.
        """
        reachable, _ = self.get_reachable_states()
        new_states = reachable[:]
        new_accepting = [s for s in self.accepting_states if s in reachable]
        new_transitions = {
            s: {sym: self.transitions[s][sym] for sym in self.alphabet}
            for s in reachable
        }
        return DFA(
            states=new_states,
            alphabet=self.alphabet[:],
            transitions=new_transitions,
            initial_state=self.initial_state,
            accepting_states=new_accepting,
        )

    def step(self, current_state: str, symbol: str) -> str:
        """Executes one single transition step delta(current_state, symbol)."""
        if current_state not in self.transitions:
            raise KeyError(f"State '{current_state}' not found in DFA transitions.")
        if symbol not in self.transitions[current_state]:
            raise KeyError(f"Symbol '{symbol}' not found in transitions for state '{current_state}'.")
        return self.transitions[current_state][symbol]

    def simulate(self, input_string: str) -> Dict[str, Any]:
        """
        Simulates an input string through the DFA.
        Returns execution trace including path, step-by-step transitions, and acceptance.
        """
        self.assert_valid()
        clean_input = str(input_string).strip()
        
        # Check alphabet membership
        for idx, char in enumerate(clean_input):
            if char not in self.alphabet:
                return {
                    "valid": False,
                    "error": f"Symbol '{char}' at index {idx} does not belong to alphabet Sigma {self.alphabet}.",
                    "input": clean_input,
                    "accepted": False,
                    "path": [],
                    "steps": [],
                }

        curr = self.initial_state
        path = [curr]
        steps = []

        for idx, sym in enumerate(clean_input):
            nxt = self.step(curr, sym)
            steps.append({
                "step_index": idx,
                "from_state": curr,
                "symbol": sym,
                "to_state": nxt,
            })
            curr = nxt
            path.append(curr)

        is_accepted = curr in self.accepting_states

        return {
            "valid": True,
            "error": None,
            "input": clean_input,
            "accepted": is_accepted,
            "final_state": curr,
            "path": path,
            "steps": steps,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializes DFA into a JSON-serializable dictionary."""
        return {
            "states": self.states,
            "alphabet": self.alphabet,
            "transitions": self.transitions,
            "initial_state": self.initial_state,
            "accepting_states": self.accepting_states,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DFA":
        """Instantiates a DFA from dictionary."""
        return cls(
            states=data.get("states", []),
            alphabet=data.get("alphabet", []),
            transitions=data.get("transitions", {}),
            initial_state=data.get("initial_state", ""),
            accepting_states=data.get("accepting_states", []),
        )

    def to_cytoscape_elements(
        self,
        partition_map: Optional[Dict[str, int]] = None,
        highlight_states: Optional[List[str]] = None,
        unreachable_states: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates Cytoscape.js compatible graph elements (nodes and edges).
        Supports partition coloring, start node badge, double borders for accepting states.
        """
        elements: List[Dict[str, Any]] = []
        highlight_set = set(highlight_states or [])
        unreachable_set = set(unreachable_states or [])
        accepting_set = set(self.accepting_states)

        # 1. Add Nodes
        for state in self.states:
            is_initial = (state == self.initial_state)
            is_accepting = (state in accepting_set)
            is_highlighted = (state in highlight_set)
            is_unreachable = (state in unreachable_set)
            partition_id = partition_map.get(state) if partition_map else None

            node_data = {
                "id": state,
                "label": state,
                "is_initial": is_initial,
                "is_accepting": is_accepting,
                "is_highlighted": is_highlighted,
                "is_unreachable": is_unreachable,
                "partition_id": partition_id,
            }
            elements.append({"group": "nodes", "data": node_data})

        # 2. Add Edges (group parallel transitions between same pair)
        # edge_groups: (source, target) -> list of symbols
        edge_groups: Dict[Tuple[str, str], List[str]] = {}
        for s in self.states:
            if s in self.transitions:
                for sym, tgt in self.transitions[s].items():
                    key = (s, tgt)
                    if key not in edge_groups:
                        edge_groups[key] = []
                    edge_groups[key].append(sym)

        for (src, tgt), syms in edge_groups.items():
            edge_label = ", ".join(sorted(syms))
            edge_id = f"e_{src}_{tgt}"
            elements.append({
                "group": "edges",
                "data": {
                    "id": edge_id,
                    "source": src,
                    "target": tgt,
                    "label": edge_label,
                    "symbols": syms,
                }
            })

        return elements
