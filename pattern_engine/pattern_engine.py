"""
PatternEngine — high-level façade that ties together the entire pipeline.

Usage::

    engine = PatternEngine()
    engine.compile("(letra|digito)+ \"@\" (letra|digito)+ \".\" letra{2,4}")
    result = engine.match("user@mail.com")         # True / False
    hits   = engine.search(long_text)               # [Match, …]
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .lexer import Lexer
from .parser import Parser
from .ast_nodes import ASTNode
from .thompson import ast_to_nfa
from .subset_construction import nfa_to_dfa
from .dfa import DFA
from .dfa_simulator import DFASimulator, Match
from .semantic_validator import validate as semantic_validate


@dataclass
class CompiledPattern:
    """A compiled pattern ready for matching."""
    name: str
    source: str
    ast: ASTNode
    dfa: DFA
    simulator: DFASimulator
    semantic_key: Optional[str] = None  # key into semantic_validator registry


class PatternEngine:
    """Compile and run mini-DSL patterns through the full pipeline."""

    def __init__(self) -> None:
        # Cache: source string → CompiledPattern
        self._cache: Dict[str, CompiledPattern] = {}

    # ── compilation ─────────────────────────────────────────────────────────

    def compile(
        self,
        source: str,
        name: str = "",
        semantic_key: Optional[str] = None,
    ) -> CompiledPattern:
        """Compile a mini-DSL expression into a DFA.

        Results are cached — calling ``compile`` twice with the same
        *source* returns the same ``CompiledPattern``.
        """
        if source in self._cache:
            return self._cache[source]

        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        sim = DFASimulator(dfa)

        compiled = CompiledPattern(
            name=name or source,
            source=source,
            ast=ast,
            dfa=dfa,
            simulator=sim,
            semantic_key=semantic_key,
        )
        self._cache[source] = compiled
        return compiled

    # ── matching ────────────────────────────────────────────────────────────

    def match(
        self,
        text: str,
        *,
        pattern: Optional[str] = None,
        compiled: Optional[CompiledPattern] = None,
    ) -> bool:
        """Return ``True`` if *text* is a full match for the pattern.

        Either *pattern* (source string) or *compiled* must be given.
        """
        cp = self._resolve(pattern, compiled)
        if not cp.simulator.full_match(text):
            return False
        # Semantic validation (if configured)
        if cp.semantic_key:
            return semantic_validate(cp.semantic_key, text)
        return True

    def search(
        self,
        text: str,
        *,
        pattern: Optional[str] = None,
        compiled: Optional[CompiledPattern] = None,
    ) -> List[Match]:
        """Find all non-overlapping matches of the pattern in *text*.

        Optionally filters out matches that fail semantic validation.
        """
        cp = self._resolve(pattern, compiled)
        raw = cp.simulator.search(text)
        if cp.semantic_key:
            return [m for m in raw if semantic_validate(cp.semantic_key, m.text)]
        return raw

    # ── helpers ─────────────────────────────────────────────────────────────

    def _resolve(
        self,
        pattern: Optional[str],
        compiled: Optional[CompiledPattern],
    ) -> CompiledPattern:
        if compiled is not None:
            return compiled
        if pattern is not None:
            return self.compile(pattern)
        raise ValueError("Either 'pattern' or 'compiled' must be provided")

    def clear_cache(self) -> None:
        """Drop all cached compiled patterns."""
        self._cache.clear()
