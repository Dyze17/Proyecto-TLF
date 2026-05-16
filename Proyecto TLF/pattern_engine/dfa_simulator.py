"""
DFA Simulator — runs the DFA against input strings.

Provides:
- ``full_match(text)`` — does the *entire* text match?
- ``search(text)``     — find *all* non-overlapping matches with positions.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .dfa import DFA, DFAState


@dataclass
class Match:
    """A single match found in the input text."""
    text: str
    start: int
    end: int       # exclusive

    def __repr__(self) -> str:
        return f"Match({self.text!r}, {self.start}:{self.end})"


class DFASimulator:
    """Simulate a DFA on input strings."""

    def __init__(self, dfa: DFA) -> None:
        self.dfa = dfa

    # ── full match ──────────────────────────────────────────────────────────

    def full_match(self, text: str) -> bool:
        """Return ``True`` if *text* is accepted as a whole by the DFA."""
        state: Optional[DFAState] = self.dfa.start
        for ch in text:
            if state is None:
                return False
            state = self.dfa.transition(state, ch)
        return state is not None and state.is_accept

    # ── search (find all matches) ──────────────────────────────────────────

    def search(self, text: str) -> List[Match]:
        """Find all non-overlapping leftmost-longest matches in *text*."""
        matches: List[Match] = []
        i = 0
        n = len(text)

        while i < n:
            best_end: Optional[int] = None
            state: Optional[DFAState] = self.dfa.start
            j = i

            # If start state is accepting, record it (handles empty match edge case)
            # We generally don't want zero-length matches though.

            while j < n and state is not None:
                state = self.dfa.transition(state, text[j])
                j += 1
                if state is not None and state.is_accept:
                    best_end = j

            if best_end is not None and best_end > i:
                matches.append(Match(text[i:best_end], i, best_end))
                i = best_end  # move past the match
            else:
                i += 1  # no match starting here, advance by one

        return matches
