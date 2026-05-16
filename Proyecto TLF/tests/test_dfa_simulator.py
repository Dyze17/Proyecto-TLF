"""Pruebas unitarias para el simulador de DFA."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.parser import parse_pattern
from pattern_engine.thompson import ast_to_nfa
from pattern_engine.subset_construction import nfa_to_dfa
from pattern_engine.dfa_simulator import DFASimulator


def _make_simulator(pattern_src: str) -> DFASimulator:
    ast = parse_pattern(pattern_src)
    nfa = ast_to_nfa(ast)
    dfa = nfa_to_dfa(nfa)
    return DFASimulator(dfa)


class TestFullMatch:
    def test_single_char(self):
        sim = _make_simulator('"a"')
        assert sim.full_match("a") is True
        assert sim.full_match("b") is False
        assert sim.full_match("") is False

    def test_concat(self):
        sim = _make_simulator('"a" "b"')
        assert sim.full_match("ab") is True
        assert sim.full_match("a") is False
        assert sim.full_match("abc") is False

    def test_union(self):
        sim = _make_simulator('"a" | "b"')
        assert sim.full_match("a") is True
        assert sim.full_match("b") is True
        assert sim.full_match("c") is False

    def test_star(self):
        sim = _make_simulator('"a"*')
        assert sim.full_match("") is True
        assert sim.full_match("a") is True
        assert sim.full_match("aaa") is True
        assert sim.full_match("ab") is False

    def test_plus(self):
        sim = _make_simulator('"a"+')
        assert sim.full_match("") is False
        assert sim.full_match("a") is True
        assert sim.full_match("aaa") is True

    def test_optional(self):
        sim = _make_simulator('"a"?')
        assert sim.full_match("") is True
        assert sim.full_match("a") is True
        assert sim.full_match("aa") is False

    def test_repeat_exact(self):
        sim = _make_simulator('"a"{3}')
        assert sim.full_match("aaa") is True
        assert sim.full_match("aa") is False
        assert sim.full_match("aaaa") is False

    def test_repeat_range(self):
        sim = _make_simulator('"a"{2,4}')
        assert sim.full_match("a") is False
        assert sim.full_match("aa") is True
        assert sim.full_match("aaa") is True
        assert sim.full_match("aaaa") is True
        assert sim.full_match("aaaaa") is False

    def test_charclass(self):
        sim = _make_simulator("letra")
        assert sim.full_match("a") is True
        assert sim.full_match("Z") is True
        assert sim.full_match("1") is False

    def test_char_range(self):
        sim = _make_simulator("[a-z]")
        assert sim.full_match("a") is True
        assert sim.full_match("z") is True
        assert sim.full_match("A") is False

    def test_complex_email(self):
        sim = _make_simulator(
            '(letra|digito|"."|"_")+ "@" (letra|digito)+ "." letra{2,4}'
        )
        assert sim.full_match("juan@mail.com") is True
        assert sim.full_match("user_99@test.org") is True
        assert sim.full_match("juan@mail") is False
        assert sim.full_match("@mail.com") is False


class TestSearch:
    def test_find_in_text(self):
        sim = _make_simulator('[A-Z]{3} "-" [0-9]{3}')
        matches = sim.search("La placa ABC-123 y XYZ-999 son válidas")
        assert len(matches) == 2
        assert matches[0].text == "ABC-123"
        assert matches[1].text == "XYZ-999"

    def test_no_matches(self):
        sim = _make_simulator('"hello"')
        matches = sim.search("world")
        assert len(matches) == 0

    def test_match_positions(self):
        sim = _make_simulator('"ab"')
        matches = sim.search("xabxab")
        assert len(matches) == 2
        assert matches[0].start == 1
        assert matches[0].end == 3
        assert matches[1].start == 4
        assert matches[1].end == 6
