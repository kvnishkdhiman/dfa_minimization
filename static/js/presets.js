/**
 * DFA Presets Library for DFA-Min Simulator.
 * Provides textbook and benchmark DFAs.
 */

const DFA_PRESETS = {
  textbook_6_state: {
    name: "Textbook 6-State DFA (Hopcroft Example)",
    description: "Standard 6-state DFA with states A, B equivalent and C, D equivalent.",
    states: ["A", "B", "C", "D", "E", "F"],
    alphabet: ["0", "1"],
    initial_state: "A",
    accepting_states: ["C", "D"],
    transitions: {
      A: { "0": "B", "1": "C" },
      B: { "0": "A", "1": "D" },
      C: { "0": "E", "1": "F" },
      D: { "0": "E", "1": "F" },
      E: { "0": "E", "1": "F" },
      F: { "0": "F", "1": "E" },
    },
  },
  unreachable_states: {
    name: "DFA with Unreachable States (U1, U2)",
    description: "States U1 and U2 cannot be reached from initial state q0 and are pruned before minimization.",
    states: ["q0", "q1", "q2", "U1", "U2"],
    alphabet: ["a", "b"],
    initial_state: "q0",
    accepting_states: ["q2", "U2"],
    transitions: {
      q0: { "a": "q1", "b": "q0" },
      q1: { "a": "q2", "b": "q1" },
      q2: { "a": "q2", "b": "q2" },
      U1: { "a": "q1", "b": "U2" },
      U2: { "a": "U1", "b": "q0" },
    },
  },
  multiple_redundancies: {
    name: "Complex 8-State DFA with Multiple Merges",
    description: "An 8-state automaton with multiple cascading equivalence classes.",
    states: ["A", "B", "C", "D", "E", "F", "G", "H"],
    alphabet: ["0", "1"],
    initial_state: "A",
    accepting_states: ["C"],
    transitions: {
      A: { "0": "B", "1": "F" },
      B: { "0": "G", "1": "C" },
      C: { "0": "A", "1": "C" },
      D: { "0": "C", "1": "G" },
      E: { "0": "H", "1": "F" },
      F: { "0": "C", "1": "G" },
      G: { "0": "G", "1": "E" },
      H: { "0": "G", "1": "C" },
    },
  },
  even_zeros_even_ones: {
    name: "Even 0s and Even 1s (Irreducible)",
    description: "Parity checker recognizing strings with even count of 0s and 1s. Already minimal.",
    states: ["qEE", "qOE", "qEO", "qOO"],
    alphabet: ["0", "1"],
    initial_state: "qEE",
    accepting_states: ["qEE"],
    transitions: {
      qEE: { "0": "qOE", "1": "qEO" },
      qOE: { "0": "qEE", "1": "qOO" },
      qEO: { "0": "qOO", "1": "qEE" },
      qOO: { "0": "qEO", "1": "qOE" },
    },
  },
  contains_01: {
    name: "Contains Substring '01'",
    description: "3-state DFA that accepts any binary string containing '01'.",
    states: ["q0", "q1", "q2"],
    alphabet: ["0", "1"],
    initial_state: "q0",
    accepting_states: ["q2"],
    transitions: {
      q0: { "0": "q1", "1": "q0" },
      q1: { "0": "q1", "1": "q2" },
      q2: { "0": "q2", "1": "q2" },
    },
  },
};
