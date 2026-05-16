"""
AST node definitions for the mini-DSL regular expression parser.

Each node represents a piece of a regular expression that can be
compiled into an NFA fragment via Thompson's construction.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, FrozenSet


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    """Abstract base for all AST nodes."""
    pass


# ---------------------------------------------------------------------------
# Leaf nodes
# ---------------------------------------------------------------------------

@dataclass
class LiteralNode(ASTNode):
    """Matches a single literal character."""
    char: str


@dataclass
class CharClassNode(ASTNode):
    """Matches any character belonging to a set (e.g. [a-z], letra, digito)."""
    chars: FrozenSet[str]
    label: str = ""  # human-readable label, e.g. "letra"


@dataclass
class AnyCharNode(ASTNode):
    """Matches any single character (`.` / `cualquier`)."""
    pass


# ---------------------------------------------------------------------------
# Composite / operator nodes
# ---------------------------------------------------------------------------

@dataclass
class ConcatNode(ASTNode):
    """Concatenation of two sub-expressions."""
    left: ASTNode
    right: ASTNode


@dataclass
class UnionNode(ASTNode):
    """Alternation (union) of two sub-expressions  (a | b)."""
    left: ASTNode
    right: ASTNode


@dataclass
class StarNode(ASTNode):
    """Kleene star — zero or more repetitions."""
    child: ASTNode


@dataclass
class PlusNode(ASTNode):
    """One or more repetitions  (sugar for child · child*)."""
    child: ASTNode


@dataclass
class OptionalNode(ASTNode):
    """Zero or one occurrence  (sugar for child | ε)."""
    child: ASTNode


@dataclass
class RepeatNode(ASTNode):
    """Bounded repetition  {min,max}.

    * ``max is None`` means unbounded (e.g. ``{2,}``).
    """
    child: ASTNode
    min_count: int
    max_count: Optional[int]  # None ⇒ unbounded
