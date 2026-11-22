"""
DFA Partition Refinement Minimization Module.
Implements the Moore / Hopcroft partition refinement algorithm with step-by-step
execution tracking, split explanations, state equivalence detection, and minimized DFA construction.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from .dfa import DFA


class DFAMinimizer:
    """
    Executes Partition Refinement DFA Minimization.
    Maintains a step-by-step log of partitions and generates the minimized DFA.
    """

    def __init__(self, dfa: DFA):
        self.original_dfa = dfa
        # Minimization is performed on reachable states
        self.dfa = dfa.filter_unreachable()
        self.history: List[Dict[str, Any]] = []
        self.final_partitions: List[List[str]] = []
        self.minimized_dfa: Optional[DFA] = None
        self.state_to_partition_map: Dict[str, int] = {}
        self.equivalent_pairs: List[Tuple[str, str]] = []

    def _state_block_index(self, state: str, partitions: List[List[str]]) -> int:
        """Finds the index of the partition block containing the given state."""
        for idx, block in enumerate(partitions):
            if state in block:
                return idx
        raise ValueError(f"State '{state}' not found in current partitions.")

    def run_all(self) -> Dict[str, Any]:
        """
        Executes the partition refinement algorithm to completion.
        Returns the complete trace, steps, equivalence classes, and minimized DFA.
        """
        self.history = []
        states = sorted(self.dfa.states)
        accepting = sorted(self.dfa.accepting_states)
        non_accepting = sorted([s for s in states if s not in set(accepting)])
        alphabet = sorted(self.dfa.alphabet)

        # Step 0: Initial Partition P0
        current_partitions: List[List[str]] = []
        if accepting and non_accepting:
            # Place partition containing initial state first (Block 0 = Blue)
            # and accepting states as Block 1 (Green)
            if self.dfa.initial_state in set(accepting):
                current_partitions = [accepting, non_accepting]
            else:
                current_partitions = [non_accepting, accepting]
            init_explanation = (
                f"Initial Partition P0: Divided into non-accepting states Q \\ F = {{{', '.join(non_accepting)}}} "
                f"and accepting states F = {{{', '.join(accepting)}}}. "
                "These cannot be equivalent because the empty string distinguishes them."
            )
        elif accepting:
            # All states are accepting
            current_partitions = [accepting]
            init_explanation = "Initial Partition P0: All states are accepting. Placed in single block."
        else:
            # No states are accepting
            current_partitions = [states]
            init_explanation = "Initial Partition P0: No states are accepting. Placed in single block."

        step_num = 0
        self.history.append({
            "step_number": step_num,
            "step_type": "initial",
            "partitions": [block[:] for block in current_partitions],
            "num_blocks": len(current_partitions),
            "explanation": init_explanation,
            "splits": [],
            "signatures": {},
            "alphabet": alphabet,
            "unreachable_pruned": self.original_dfa.get_reachable_states()[1],
            "is_stable": False,
        })

        is_stable = False
        while not is_stable:
            step_num += 1
            next_partitions: List[List[str]] = []
            splits_in_step: List[Dict[str, Any]] = []
            signatures_in_step: Dict[str, Any] = {}
            any_block_split = False

            for block_idx, block in enumerate(current_partitions):
                if len(block) <= 1:
                    # Single state block cannot be split
                    next_partitions.append(block[:])
                    continue

                # Compute signature for each state in block:
                # Signature is tuple of target block indices for each symbol in alphabet
                sig_groups: Dict[Tuple[int, ...], List[str]] = defaultdict(list)
                state_details: Dict[str, Dict[str, Any]] = {}

                for state in block:
                    targets: List[int] = []
                    symbol_dest_info: Dict[str, Dict[str, Any]] = {}
                    for sym in alphabet:
                        target_state = self.dfa.transitions[state][sym]
                        target_block_idx = self._state_block_index(target_state, current_partitions)
                        targets.append(target_block_idx)
                        symbol_dest_info[sym] = {
                            "target_state": target_state,
                            "target_block_idx": target_block_idx,
                            "target_block_label": f"P{target_block_idx} {{{', '.join(current_partitions[target_block_idx])}}}",
                        }

                    sig_tuple = tuple(targets)
                    sig_groups[sig_tuple].append(state)
                    sig_label = "(" + ", ".join([f"P{t}" for t in targets]) + ")"
                    state_details[state] = {
                        "targets": targets,
                        "signature_label": sig_label,
                        "by_symbol": symbol_dest_info,
                    }

                signatures_in_step[f"Block_{block_idx}"] = {
                    "block_index": block_idx,
                    "block_label": f"P{block_idx}",
                    "original_block": block[:],
                    "state_details": state_details,
                    "did_split": len(sig_groups) > 1,
                    "groups_count": len(sig_groups),
                    "sub_blocks": [sorted(grp) for grp in sig_groups.values()],
                }

                if len(sig_groups) > 1:
                    # Block is split!
                    any_block_split = True
                    sub_blocks = [sorted(grp) for grp in sig_groups.values()]
                    # Keep ordering consistent
                    sub_blocks.sort(key=lambda b: (b[0] if b else ""))
                    next_partitions.extend(sub_blocks)

                    # Explain why this block split
                    split_desc = (
                        f"Block {{{', '.join(block)}}} split into {len(sub_blocks)} sub-blocks: "
                        + ", ".join([f"{{{', '.join(sb)}}}" for sb in sub_blocks])
                        + " due to differing transition targets on input symbols."
                    )
                    splits_in_step.append({
                        "original_block": block[:],
                        "sub_blocks": sub_blocks,
                        "description": split_desc,
                    })
                else:
                    # Block remained unified
                    next_partitions.append(block[:])

            # Sort next partitions deterministically:
            # Priority 0: Contains initial state (always Block 0 -> Blue)
            # Priority 1: Accepting blocks (Block 1 -> Green)
            # Priority 2: Other blocks
            def _partition_sort_key(b: List[str]):
                if self.dfa.initial_state in b:
                    return (0, b[0] if b else "")
                elif any(s in self.dfa.accepting_states for s in b):
                    return (1, b[0] if b else "")
                else:
                    return (2, b[0] if b else "")

            next_partitions.sort(key=_partition_sort_key)

            if not any_block_split:
                is_stable = True
                explanation = (
                    f"Step {step_num}: No partition block could be split further. "
                    "The partition is stable and forms the final equivalence classes."
                )
            else:
                explanation = (
                    f"Step {step_num}: Refined partitions from {len(current_partitions)} blocks "
                    f"to {len(next_partitions)} blocks based on outgoing transitions."
                )

            self.history.append({
                "step_number": step_num,
                "step_type": "fixed_point" if is_stable else "refinement",
                "partitions": [b[:] for b in next_partitions],
                "num_blocks": len(next_partitions),
                "explanation": explanation,
                "splits": splits_in_step,
                "signatures": signatures_in_step,
                "alphabet": alphabet,
                "is_stable": is_stable,
            })

            current_partitions = next_partitions

        # Final equivalence classes
        self.final_partitions = current_partitions
        self._detect_equivalent_pairs()
        self._construct_minimized_dfa()

        return {
            "success": True,
            "steps": self.history,
            "total_steps": len(self.history),
            "original_states_count": len(self.original_dfa.states),
            "reachable_states_count": len(self.dfa.states),
            "unreachable_states": self.original_dfa.get_reachable_states()[1],
            "minimized_states_count": len(self.final_partitions),
            "equivalence_classes": self.final_partitions,
            "equivalent_pairs": self.equivalent_pairs,
            "minimized_dfa": self.minimized_dfa.to_dict() if self.minimized_dfa else None,
            "minimized_elements": self.minimized_dfa.to_cytoscape_elements() if self.minimized_dfa else [],
        }

    def _detect_equivalent_pairs(self) -> None:
        """Finds all pairs of distinct states that are equivalent (belong to same final block)."""
        self.equivalent_pairs = []
        for block in self.final_partitions:
            if len(block) > 1:
                sorted_block = sorted(block)
                for i in range(len(sorted_block)):
                    for j in range(i + 1, len(sorted_block)):
                        self.equivalent_pairs.append((sorted_block[i], sorted_block[j]))

    def _construct_minimized_dfa(self) -> None:
        """
        Constructs the minimal equivalent DFA from the final partition equivalence classes.
        """
        alphabet = sorted(self.dfa.alphabet)
        
        # Build mapping from original state to new minimized state name
        min_state_names: List[str] = []
        min_state_labels: Dict[str, str] = {}
        state_to_min_map: Dict[str, str] = {}
        min_initial_state = ""
        min_accepting_states: List[str] = []

        for idx, block in enumerate(self.final_partitions):
            # Create a clean readable identifier e.g. "[A, B]" or "q_{A_B}"
            sorted_block = sorted(block)
            name = f"[{','.join(sorted_block)}]"
            label = f"{{{','.join(sorted_block)}}}"
            min_state_names.append(name)
            min_state_labels[name] = label

            for s in sorted_block:
                state_to_min_map[s] = name

            # Initial state: the block containing q0
            if self.dfa.initial_state in block:
                min_initial_state = name

            # Accepting state: any block containing an accepting state
            if any(s in self.dfa.accepting_states for s in block):
                min_accepting_states.append(name)

        # Minimized transitions: delta'([q], a) = [delta(q, a)]
        min_transitions: Dict[str, Dict[str, str]] = {}
        for block in self.final_partitions:
            rep = block[0]  # representative state from the equivalence class
            min_name = state_to_min_map[rep]
            min_transitions[min_name] = {}
            for sym in alphabet:
                orig_target = self.dfa.transitions[rep][sym]
                min_target = state_to_min_map[orig_target]
                min_transitions[min_name][sym] = min_target

        self.minimized_dfa = DFA(
            states=min_state_names,
            alphabet=alphabet,
            transitions=min_transitions,
            initial_state=min_initial_state,
            accepting_states=min_accepting_states,
        )
