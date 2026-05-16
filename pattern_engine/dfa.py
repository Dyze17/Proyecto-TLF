"""
DFA (Deterministic Finite Automaton) data structures.

The DFA is produced by subset construction from an NFA and is used
by the simulator to accept / reject input strings.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional, Set


class DFAState:
    """A single state in the DFA.

    Each DFA state corresponds to a *set* of NFA states (produced by
    subset construction).
    """

    _counter: int = 0

    def __init__(
        self,
        nfa_state_ids: FrozenSet[int],
        is_accept: bool = False,
    ) -> None:
        DFAState._counter += 1
        self.id: int = DFAState._counter
        self.nfa_state_ids: FrozenSet[int] = nfa_state_ids
        self.is_accept: bool = is_accept
        # symbol → destination DFAState
        self.transitions: Dict[str, DFAState] = {}

    def add_transition(self, symbol: str, target: DFAState) -> None:
        self.transitions[symbol] = target

    def __repr__(self) -> str:
        return f"DFAState({self.id}, accept={self.is_accept})"

    def __hash__(self) -> int:
        return hash(self.nfa_state_ids)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DFAState):
            return NotImplemented
        return self.nfa_state_ids == other.nfa_state_ids


class DFA:
    """Complete DFA ready for simulation."""

    def __init__(
        self,
        start: DFAState,
        states: Set[DFAState],
        accept_states: Set[DFAState],
        alphabet: Set[str],
    ) -> None:
        self.start = start
        self.states = states
        self.accept_states = accept_states
        self.alphabet = alphabet

    def transition(self, state: DFAState, symbol: str) -> Optional[DFAState]:
        """Return the target state for *symbol* from *state*, or ``None``."""
        return state.transitions.get(symbol)
