"""
DFA-Min: Interactive Automata Minimization and State Equivalence Simulator
Automata package initialization.
"""

from .dfa import DFA
from .minimizer import DFAMinimizer
from .distinguisher import DistinguishingStringFinder
from .equivalence import LanguageEquivalenceChecker

__all__ = [
    "DFA",
    "DFAMinimizer",
    "DistinguishingStringFinder",
    "LanguageEquivalenceChecker",
]
