"""
Lexer (tokenizer) for the mini-DSL used to define patterns.

Supported syntax
----------------
- **Keywords**:  ``letra``, ``digito``, ``espacio``, ``cualquier``
- **Literals**:  ``"@"``, ``"."``, single unquoted printable chars
- **Char classes**: ``[a-z]``, ``[A-Z]``, ``[0-9]``, ``[a-zA-Z]``
- **Operators**:  ``|``, ``+``, ``*``, ``?``
- **Grouping**:   ``(``, ``)``
- **Repetition**: ``{n}``, ``{n,}``, ``{n,m}``

Example DSL expression::

    (letra|digito|"."|"_")+ "@" (letra|digito)+ "." letra{2,4}
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


# ── Token types ──────────────────────────────────────────────────────────────

class TokenType(Enum):
    LITERAL    = auto()   # a single character to match
    CHARCLASS  = auto()   # a named class: letra, digito, espacio
    ANYCHAR    = auto()   # cualquier / .
    PIPE       = auto()   # |
    STAR       = auto()   # *
    PLUS       = auto()   # +
    QUESTION   = auto()   # ?
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACE     = auto()   # {   (start of repetition)
    RBRACE     = auto()   # }
    COMMA      = auto()   # ,   (inside repetition)
    NUMBER     = auto()   # integer inside {n,m}
    CHARRANGE  = auto()   # character-range set from [a-z] etc.
    EOF        = auto()


@dataclass
class Token:
    type: TokenType
    value: str      # original text
    pos: int        # position in source string

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.pos})"


# ── Built-in character classes ───────────────────────────────────────────────

import string as _string

KEYWORDS: dict[str, frozenset[str]] = {
    "letra":    frozenset(_string.ascii_letters),
    "digito":   frozenset(_string.digits),
    "espacio":  frozenset(" \t\n\r"),
}

# ── Lexer ────────────────────────────────────────────────────────────────────

class LexerError(Exception):
    """Raised when the lexer encounters unexpected input."""
    def __init__(self, message: str, pos: int) -> None:
        super().__init__(message)
        self.pos = pos


class Lexer:
    """Tokenize a mini-DSL pattern string."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.tokens: List[Token] = []

    # -- public API ----------------------------------------------------------

    def tokenize(self) -> List[Token]:
        """Return the complete token list (including EOF)."""
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break
            ch = self.source[self.pos]

            if ch == '"':
                self._read_quoted_literal()
            elif ch == '[':
                self._read_char_range()
            elif ch == '{':
                self._read_repetition()
            elif ch == '(':
                self._emit(TokenType.LPAREN, ch)
            elif ch == ')':
                self._emit(TokenType.RPAREN, ch)
            elif ch == '|':
                self._emit(TokenType.PIPE, ch)
            elif ch == '*':
                self._emit(TokenType.STAR, ch)
            elif ch == '+':
                self._emit(TokenType.PLUS, ch)
            elif ch == '?':
                self._emit(TokenType.QUESTION, ch)
            elif ch == '.':
                # A dot outside quotes is an ANYCHAR
                self._emit(TokenType.ANYCHAR, ch)
            elif ch.isalpha():
                self._read_keyword_or_literal()
            elif ch.isdigit():
                # Bare digit treated as literal
                self._emit(TokenType.LITERAL, ch)
            else:
                # Any other printable character is a literal
                self._emit(TokenType.LITERAL, ch)

        self.tokens.append(Token(TokenType.EOF, "", self.pos))
        return self.tokens

    # -- internal helpers ----------------------------------------------------

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t'):
            self.pos += 1

    def _emit(self, ttype: TokenType, value: str) -> None:
        self.tokens.append(Token(ttype, value, self.pos))
        self.pos += len(value)

    def _read_quoted_literal(self) -> None:
        """Read a double-quoted literal string and emit one LITERAL token per character."""
        start = self.pos
        self.pos += 1  # skip opening "
        buf: list[str] = []
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\\':
                self.pos += 1
                if self.pos >= len(self.source):
                    raise LexerError("Unexpected end of string after backslash", self.pos)
                escape_map = {'n': '\n', 't': '\t', '\\': '\\', '"': '"'}
                ch = self.source[self.pos]
                buf.append(escape_map.get(ch, ch))
            else:
                buf.append(self.source[self.pos])
            self.pos += 1
        if self.pos >= len(self.source):
            raise LexerError("Unterminated string literal", start)
        self.pos += 1  # skip closing "
        for c in buf:
            self.tokens.append(Token(TokenType.LITERAL, c, start))

    def _read_char_range(self) -> None:
        """Read ``[a-zA-Z0-9]`` style character classes."""
        start = self.pos
        self.pos += 1  # skip [
        chars: set[str] = set()
        while self.pos < len(self.source) and self.source[self.pos] != ']':
            lo = self.source[self.pos]
            if (
                self.pos + 2 < len(self.source)
                and self.source[self.pos + 1] == '-'
                and self.source[self.pos + 2] != ']'
            ):
                hi = self.source[self.pos + 2]
                for o in range(ord(lo), ord(hi) + 1):
                    chars.add(chr(o))
                self.pos += 3
            else:
                chars.add(lo)
                self.pos += 1
        if self.pos >= len(self.source):
            raise LexerError("Unterminated character class", start)
        self.pos += 1  # skip ]
        self.tokens.append(Token(TokenType.CHARRANGE, "".join(sorted(chars)), start))

    def _read_repetition(self) -> None:
        """Read ``{n}``, ``{n,}``, ``{n,m}``."""
        self.tokens.append(Token(TokenType.LBRACE, "{", self.pos))
        self.pos += 1
        self._skip_whitespace()
        # first number
        num_start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        if self.pos == num_start:
            raise LexerError("Expected number after '{'", self.pos)
        self.tokens.append(Token(TokenType.NUMBER, self.source[num_start:self.pos], num_start))
        self._skip_whitespace()
        if self.pos < len(self.source) and self.source[self.pos] == ',':
            self.tokens.append(Token(TokenType.COMMA, ",", self.pos))
            self.pos += 1
            self._skip_whitespace()
            # optional second number
            num_start = self.pos
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self.pos += 1
            if self.pos > num_start:
                self.tokens.append(Token(TokenType.NUMBER, self.source[num_start:self.pos], num_start))
            self._skip_whitespace()
        if self.pos >= len(self.source) or self.source[self.pos] != '}':
            raise LexerError("Expected '}' to close repetition", self.pos)
        self.tokens.append(Token(TokenType.RBRACE, "}", self.pos))
        self.pos += 1

    def _read_keyword_or_literal(self) -> None:
        """Read an identifier and check if it is a keyword."""
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isalpha():
            self.pos += 1
        word = self.source[start:self.pos]
        if word in KEYWORDS:
            self.tokens.append(Token(TokenType.CHARCLASS, word, start))
        elif word == "cualquier":
            self.tokens.append(Token(TokenType.ANYCHAR, word, start))
        else:
            # Treat each character as a separate literal (implicit concatenation)
            for i, c in enumerate(word):
                self.tokens.append(Token(TokenType.LITERAL, c, start + i))
