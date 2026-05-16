"""
Thompson's construction — converts an AST into an NFA.

Every AST node produces a small NFA *fragment* (start, accept).
Fragments are composed using ε-transitions to build the full NFA.
"""

from __future__ import annotations
import string as _string
from typing import FrozenSet

from .ast_nodes import (
    ASTNode,
    LiteralNode,
    CharClassNode,
    AnyCharNode,
    ConcatNode,
    UnionNode,
    StarNode,
    PlusNode,
    OptionalNode,
    RepeatNode,
)
from .nfa import NFA, NFAFragment, NFAState

# All printable ASCII characters used for AnyCharNode matching
_ALL_PRINTABLE: FrozenSet[str] = frozenset(
    _string.ascii_letters + _string.digits + _string.punctuation + " "
)


def _build_fragment(node: ASTNode) -> NFAFragment:
    """Recursively build an NFA fragment for *node*."""

    if isinstance(node, LiteralNode):
        return _literal(node.char)

    if isinstance(node, CharClassNode):
        return _char_class(node.chars)

    if isinstance(node, AnyCharNode):
        return _char_class(_ALL_PRINTABLE)

    if isinstance(node, ConcatNode):
        return _concat(
            _build_fragment(node.left),
            _build_fragment(node.right),
        )

    if isinstance(node, UnionNode):
        return _union(
            _build_fragment(node.left),
            _build_fragment(node.right),
        )

    if isinstance(node, StarNode):
        return _star(_build_fragment(node.child))

    if isinstance(node, PlusNode):
        return _plus(_build_fragment(node.child))

    if isinstance(node, OptionalNode):
        return _optional(_build_fragment(node.child))

    if isinstance(node, RepeatNode):
        return _repeat(node)

    raise TypeError(f"Unknown AST node type: {type(node)}")


# ── Fragment constructors ────────────────────────────────────────────────────

def _literal(char: str) -> NFAFragment:
    """Match a single character."""
    start = NFAState()
    accept = NFAState(is_accept=True)
    start.add_transition(char, accept)
    return NFAFragment(start, accept)


def _char_class(chars: FrozenSet[str]) -> NFAFragment:
    """Match any character in *chars* (e.g. ``letra``, ``[a-z]``)."""
    start = NFAState()
    accept = NFAState(is_accept=True)
    for ch in chars:
        start.add_transition(ch, accept)
    return NFAFragment(start, accept)


def _concat(frag_a: NFAFragment, frag_b: NFAFragment) -> NFAFragment:
    """Concatenation: A · B"""
    frag_a.accept.is_accept = False
    frag_a.accept.add_transition("", frag_b.start)
    return NFAFragment(frag_a.start, frag_b.accept)


def _union(frag_a: NFAFragment, frag_b: NFAFragment) -> NFAFragment:
    """Union: A | B"""
    start = NFAState()
    accept = NFAState(is_accept=True)
    start.add_transition("", frag_a.start)
    start.add_transition("", frag_b.start)
    frag_a.accept.is_accept = False
    frag_a.accept.add_transition("", accept)
    frag_b.accept.is_accept = False
    frag_b.accept.add_transition("", accept)
    return NFAFragment(start, accept)


def _star(frag: NFAFragment) -> NFAFragment:
    """Kleene star: A*"""
    start = NFAState()
    accept = NFAState(is_accept=True)
    start.add_transition("", frag.start)
    start.add_transition("", accept)
    frag.accept.is_accept = False
    frag.accept.add_transition("", frag.start)
    frag.accept.add_transition("", accept)
    return NFAFragment(start, accept)


def _plus(frag: NFAFragment) -> NFAFragment:
    """One or more: A+  ≡  A · A*"""
    start = NFAState()
    accept = NFAState(is_accept=True)
    start.add_transition("", frag.start)
    frag.accept.is_accept = False
    frag.accept.add_transition("", frag.start)
    frag.accept.add_transition("", accept)
    return NFAFragment(start, accept)


def _optional(frag: NFAFragment) -> NFAFragment:
    """Optional: A?  ≡  A | ε"""
    start = NFAState()
    accept = NFAState(is_accept=True)
    start.add_transition("", frag.start)
    start.add_transition("", accept)
    frag.accept.is_accept = False
    frag.accept.add_transition("", accept)
    return NFAFragment(start, accept)


def _repeat(node: RepeatNode) -> NFAFragment:
    """Bounded repetition: A{min,max}.

    Strategy:
    - Concatenate *min* mandatory copies.
    - Append *max - min* optional copies (or star for unbounded).
    """
    min_c = node.min_count
    max_c = node.max_count

    # Build at least one fragment to get the shape
    if min_c == 0 and max_c == 0:
        # {0,0} ⇒ match empty string
        start = NFAState()
        accept = NFAState(is_accept=True)
        start.add_transition("", accept)
        return NFAFragment(start, accept)

    # Mandatory copies
    parts: list[NFAFragment] = []
    for _ in range(min_c):
        parts.append(_build_fragment(node.child))

    if max_c is None:
        # {min,} ⇒ mandatory copies + star
        parts.append(_star(_build_fragment(node.child)))
    else:
        # optional copies for (max - min)
        for _ in range(max_c - min_c):
            parts.append(_optional(_build_fragment(node.child)))

    if not parts:
        # Edge case: {0} with bounded 0
        start = NFAState()
        accept = NFAState(is_accept=True)
        start.add_transition("", accept)
        return NFAFragment(start, accept)

    # Concatenate all parts
    result = parts[0]
    for p in parts[1:]:
        result = _concat(result, p)

    return result


# ── Public API ───────────────────────────────────────────────────────────────

def ast_to_nfa(ast: ASTNode) -> NFA:
    """Convert an AST tree into a complete NFA."""
    # Reset state counter for reproducibility in tests
    NFAState._counter = 0
    frag = _build_fragment(ast)
    frag.accept.is_accept = True
    return NFA(frag.start, frag.accept)
