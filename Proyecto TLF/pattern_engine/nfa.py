"""
NFA (Non-deterministic Finite Automaton) data structures.

An NFA is built from *fragments* during Thompson's construction.
Each state stores its outgoing transitions as:
  - symbol transitions:  char → {state, …}
  - epsilon transitions: ε   → {state, …}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set


EPSILON = ""  # sentinel for ε-transitions


class NFAState:
    """A single state in the NFA."""

    _counter: int = 0  # class-level auto-id

    def __init__(self, is_accept: bool = False) -> None:
        NFAState._counter += 1
        self.id: int = NFAState._counter
        self.is_accept: bool = is_accept
        # char → set of destination states
        self.transitions: Dict[str, Set[NFAState]] = {}
        # ε-transitions
        self.epsilon_transitions: Set[NFAState] = set()

    def add_transition(self, symbol: str, target: NFAState) -> None:
        if symbol == EPSILON:
            self.epsilon_transitions.add(target)
        else:
            self.transitions.setdefault(symbol, set()).add(target)

    def __repr__(self) -> str:
        return f"NFAState({self.id}, accept={self.is_accept})"

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NFAState):
            return NotImplemented
        return self.id == other.id


@dataclass
class NFAFragment:
    """A fragment of an NFA with a single start state and single accept state.

    Thompson's construction produces one fragment per AST node and then
    connects them together.
    """
    start: NFAState
    accept: NFAState


class NFA:
    """Complete NFA ready for subset construction."""

    def __init__(self, start: NFAState, accept: NFAState) -> None:
        self.start = start
        self.accept = accept

    # ----- helpers ----------------------------------------------------------

    def _collect_states(self) -> Set[NFAState]:
        """BFS / DFS to collect every reachable state."""
        visited: Set[NFAState] = set()
        stack: List[NFAState] = [self.start]
        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)
            for targets in s.transitions.values():
                stack.extend(targets)
            stack.extend(s.epsilon_transitions)
        return visited

    @property
    def states(self) -> Set[NFAState]:
        return self._collect_states()

    def alphabet(self) -> Set[str]:
        """Return the set of all input symbols (excluding ε)."""
        symbols: Set[str] = set()
        for state in self.states:
            symbols.update(state.transitions.keys())
        return symbols
