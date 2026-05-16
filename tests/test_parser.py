"""Pruebas unitarias para el parser."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.parser import parse_pattern, ParserError
from pattern_engine.ast_nodes import (
    LiteralNode, CharClassNode, ConcatNode, UnionNode,
    StarNode, PlusNode, OptionalNode, RepeatNode, AnyCharNode,
)
import pytest


class TestParserAtoms:
    def test_single_literal(self):
        ast = parse_pattern('"a"')
        assert isinstance(ast, LiteralNode)
        assert ast.char == "a"

    def test_charclass_letra(self):
        ast = parse_pattern("letra")
        assert isinstance(ast, CharClassNode)
        assert ast.label == "letra"

    def test_anychar(self):
        ast = parse_pattern("cualquier")
        assert isinstance(ast, AnyCharNode)

    def test_char_range(self):
        ast = parse_pattern("[a-z]")
        assert isinstance(ast, CharClassNode)


class TestParserOperators:
    def test_concat(self):
        ast = parse_pattern('"a" "b"')
        assert isinstance(ast, ConcatNode)
        assert isinstance(ast.left, LiteralNode)
        assert isinstance(ast.right, LiteralNode)

    def test_union(self):
        ast = parse_pattern('"a" | "b"')
        assert isinstance(ast, UnionNode)

    def test_star(self):
        ast = parse_pattern('"a"*')
        assert isinstance(ast, StarNode)

    def test_plus(self):
        ast = parse_pattern('"a"+')
        assert isinstance(ast, PlusNode)

    def test_optional(self):
        ast = parse_pattern('"a"?')
        assert isinstance(ast, OptionalNode)

    def test_repeat_exact(self):
        ast = parse_pattern('"a"{3}')
        assert isinstance(ast, RepeatNode)
        assert ast.min_count == 3
        assert ast.max_count == 3

    def test_repeat_range(self):
        ast = parse_pattern('"a"{2,4}')
        assert isinstance(ast, RepeatNode)
        assert ast.min_count == 2
        assert ast.max_count == 4

    def test_repeat_unbounded(self):
        ast = parse_pattern('"a"{1,}')
        assert isinstance(ast, RepeatNode)
        assert ast.min_count == 1
        assert ast.max_count is None


class TestParserGrouping:
    def test_grouped_union(self):
        ast = parse_pattern('("a" | "b") "c"')
        assert isinstance(ast, ConcatNode)
        assert isinstance(ast.left, UnionNode)
        assert isinstance(ast.right, LiteralNode)

    def test_nested_groups(self):
        ast = parse_pattern('(("a"))')
        assert isinstance(ast, LiteralNode)


class TestParserErrors:
    def test_unexpected_rparen(self):
        with pytest.raises(ParserError):
            parse_pattern(")")

    def test_missing_rparen(self):
        with pytest.raises(ParserError):
            parse_pattern('("a"')
