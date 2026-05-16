"""
Recursive-descent parser for the mini-DSL.

Grammar (informal)::

    expr    → term ( '|' term )*
    term    → factor+
    factor  → atom quantifier?
    atom    → LITERAL | CHARCLASS | CHARRANGE | ANYCHAR | '(' expr ')'
    quantifier → '*' | '+' | '?' | '{' n '}' | '{' n ',' '}' | '{' n ',' m '}'
"""

from __future__ import annotations
from typing import List, Optional

from .lexer import Token, TokenType, Lexer
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
from .lexer import KEYWORDS


class ParserError(Exception):
    """Raised when the parser encounters unexpected syntax."""
    def __init__(self, message: str, pos: int) -> None:
        super().__init__(message)
        self.pos = pos


class Parser:
    """Build an AST from a list of tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # -- public API ----------------------------------------------------------

    def parse(self) -> ASTNode:
        node = self._parse_expr()
        if self._current().type != TokenType.EOF:
            raise ParserError(
                f"Unexpected token {self._current()!r}",
                self._current().pos,
            )
        return node

    # -- recursive descent ---------------------------------------------------

    def _parse_expr(self) -> ASTNode:
        """expr → term ( '|' term )*"""
        node = self._parse_term()
        while self._current().type == TokenType.PIPE:
            self._advance()  # consume '|'
            right = self._parse_term()
            node = UnionNode(node, right)
        return node

    def _parse_term(self) -> ASTNode:
        """term → factor+"""
        node = self._parse_factor()
        while self._current().type in (
            TokenType.LITERAL,
            TokenType.CHARCLASS,
            TokenType.CHARRANGE,
            TokenType.ANYCHAR,
            TokenType.LPAREN,
        ):
            right = self._parse_factor()
            node = ConcatNode(node, right)
        return node

    def _parse_factor(self) -> ASTNode:
        """factor → atom quantifier?"""
        node = self._parse_atom()
        node = self._parse_quantifier(node)
        return node

    def _parse_atom(self) -> ASTNode:
        """atom → LITERAL | CHARCLASS | CHARRANGE | ANYCHAR | '(' expr ')'"""
        tok = self._current()

        if tok.type == TokenType.LITERAL:
            self._advance()
            return LiteralNode(tok.value)

        if tok.type == TokenType.CHARCLASS:
            self._advance()
            return CharClassNode(KEYWORDS[tok.value], label=tok.value)

        if tok.type == TokenType.CHARRANGE:
            self._advance()
            return CharClassNode(frozenset(tok.value), label=f"[{tok.value}]")

        if tok.type == TokenType.ANYCHAR:
            self._advance()
            return AnyCharNode()

        if tok.type == TokenType.LPAREN:
            self._advance()  # consume '('
            node = self._parse_expr()
            if self._current().type != TokenType.RPAREN:
                raise ParserError(
                    "Expected ')'",
                    self._current().pos,
                )
            self._advance()  # consume ')'
            return node

        raise ParserError(
            f"Unexpected token {tok!r} (expected atom)",
            tok.pos,
        )

    def _parse_quantifier(self, node: ASTNode) -> ASTNode:
        """quantifier → '*' | '+' | '?' | '{n}' | '{n,}' | '{n,m}'"""
        tok = self._current()

        if tok.type == TokenType.STAR:
            self._advance()
            return StarNode(node)

        if tok.type == TokenType.PLUS:
            self._advance()
            return PlusNode(node)

        if tok.type == TokenType.QUESTION:
            self._advance()
            return OptionalNode(node)

        if tok.type == TokenType.LBRACE:
            return self._parse_repetition(node)

        return node  # no quantifier

    def _parse_repetition(self, node: ASTNode) -> ASTNode:
        self._expect(TokenType.LBRACE)
        min_tok = self._expect(TokenType.NUMBER)
        min_count = int(min_tok.value)
        max_count: Optional[int] = min_count  # default: exact {n}

        if self._current().type == TokenType.COMMA:
            self._advance()  # consume ','
            if self._current().type == TokenType.NUMBER:
                max_tok = self._current()
                self._advance()
                max_count = int(max_tok.value)
            else:
                max_count = None  # unbounded {n,}

        self._expect(TokenType.RBRACE)
        return RepeatNode(node, min_count, max_count)

    # -- helpers -------------------------------------------------------------

    def _current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        # Should not happen if tokenizer emits EOF, but just in case
        return Token(TokenType.EOF, "", -1)

    def _advance(self) -> Token:
        tok = self._current()
        self.pos += 1
        return tok

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._current()
        if tok.type != ttype:
            raise ParserError(
                f"Expected {ttype.name} but got {tok!r}",
                tok.pos,
            )
        self._advance()
        return tok


# ── Convenience function ─────────────────────────────────────────────────────

def parse_pattern(source: str) -> ASTNode:
    """Lex + parse a mini-DSL pattern and return the AST root."""
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()
