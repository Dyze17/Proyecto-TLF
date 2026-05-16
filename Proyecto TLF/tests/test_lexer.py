"""Pruebas unitarias para el lexer."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.lexer import Lexer, TokenType, LexerError
import pytest


class TestLexerBasics:
    def test_empty_input(self):
        tokens = Lexer("").tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_single_literal_quoted(self):
        tokens = Lexer('"a"').tokenize()
        assert tokens[0].type == TokenType.LITERAL
        assert tokens[0].value == "a"

    def test_keyword_letra(self):
        tokens = Lexer("letra").tokenize()
        assert tokens[0].type == TokenType.CHARCLASS
        assert tokens[0].value == "letra"

    def test_keyword_digito(self):
        tokens = Lexer("digito").tokenize()
        assert tokens[0].type == TokenType.CHARCLASS
        assert tokens[0].value == "digito"

    def test_keyword_cualquier(self):
        tokens = Lexer("cualquier").tokenize()
        assert tokens[0].type == TokenType.ANYCHAR

    def test_operators(self):
        tokens = Lexer("| * + ?").tokenize()
        types = [t.type for t in tokens[:-1]]  # exclude EOF
        assert types == [TokenType.PIPE, TokenType.STAR, TokenType.PLUS, TokenType.QUESTION]

    def test_parens(self):
        tokens = Lexer("(letra)").tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [TokenType.LPAREN, TokenType.CHARCLASS, TokenType.RPAREN]

    def test_char_range(self):
        tokens = Lexer("[a-z]").tokenize()
        assert tokens[0].type == TokenType.CHARRANGE

    def test_repetition_exact(self):
        tokens = Lexer("{3}").tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [TokenType.LBRACE, TokenType.NUMBER, TokenType.RBRACE]
        assert tokens[1].value == "3"

    def test_repetition_range(self):
        tokens = Lexer("{2,4}").tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [
            TokenType.LBRACE, TokenType.NUMBER, TokenType.COMMA,
            TokenType.NUMBER, TokenType.RBRACE,
        ]

    def test_repetition_unbounded(self):
        tokens = Lexer("{1,}").tokenize()
        types = [t.type for t in tokens[:-1]]
        assert types == [
            TokenType.LBRACE, TokenType.NUMBER, TokenType.COMMA,
            TokenType.RBRACE,
        ]


class TestLexerComplex:
    def test_email_pattern(self):
        src = '(letra|digito|"."|"_")+ "@" (letra|digito)+ "." letra{2,4}'
        tokens = Lexer(src).tokenize()
        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF
        # Check some key tokens
        types = [t.type for t in tokens]
        assert TokenType.PIPE in types
        assert TokenType.PLUS in types

    def test_unterminated_string(self):
        with pytest.raises(LexerError):
            Lexer('"hello').tokenize()

    def test_unknown_word_as_literals(self):
        tokens = Lexer("abc").tokenize()
        # Unknown word should be split into literals
        assert all(t.type == TokenType.LITERAL for t in tokens[:-1])
        assert [t.value for t in tokens[:-1]] == ["a", "b", "c"]
