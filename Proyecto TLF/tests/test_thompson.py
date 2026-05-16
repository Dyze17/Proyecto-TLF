"""Pruebas unitarias para la construcción de Thompson (AST → NFA)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.parser import parse_pattern
from pattern_engine.thompson import ast_to_nfa


class TestThompson:
    def test_single_literal_nfa(self):
        ast = parse_pattern('"a"')
        nfa = ast_to_nfa(ast)
        assert nfa.start is not None
        assert nfa.accept is not None
        assert nfa.accept.is_accept

    def test_literal_transitions(self):
        ast = parse_pattern('"a"')
        nfa = ast_to_nfa(ast)
        # Start should have a transition on 'a'
        assert "a" in nfa.start.transitions
        targets = nfa.start.transitions["a"]
        assert nfa.accept in targets

    def test_concat_nfa(self):
        ast = parse_pattern('"a" "b"')
        nfa = ast_to_nfa(ast)
        # Should have states for both 'a' and 'b'
        states = nfa.states
        assert len(states) >= 4  # at least 4 states for a·b

    def test_union_nfa(self):
        ast = parse_pattern('"a" | "b"')
        nfa = ast_to_nfa(ast)
        # Start should have epsilon transitions
        assert len(nfa.start.epsilon_transitions) == 2

    def test_star_nfa(self):
        ast = parse_pattern('"a"*')
        nfa = ast_to_nfa(ast)
        # Start should have epsilon to accept (match empty)
        assert nfa.accept.id in {s.id for s in nfa.start.epsilon_transitions}

    def test_charclass_nfa(self):
        ast = parse_pattern("letra")
        nfa = ast_to_nfa(ast)
        # Should have transitions for all letters
        assert len(nfa.start.transitions) == 52  # a-z + A-Z

    def test_alphabet(self):
        ast = parse_pattern('"a" | "b"')
        nfa = ast_to_nfa(ast)
        alpha = nfa.alphabet()
        assert "a" in alpha
        assert "b" in alpha
