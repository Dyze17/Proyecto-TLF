"""Pruebas unitarias para la construcción de subconjuntos (NFA → DFA)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.parser import parse_pattern
from pattern_engine.thompson import ast_to_nfa
from pattern_engine.subset_construction import nfa_to_dfa


class TestSubsetConstruction:
    def test_single_literal_dfa(self):
        ast = parse_pattern('"a"')
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        assert dfa.start is not None
        assert len(dfa.accept_states) >= 1
        assert dfa.alphabet == {"a"}

    def test_union_dfa(self):
        ast = parse_pattern('"a" | "b"')
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        assert "a" in dfa.alphabet
        assert "b" in dfa.alphabet
        # Both 'a' and 'b' should lead to accept
        sa = dfa.transition(dfa.start, "a")
        sb = dfa.transition(dfa.start, "b")
        assert sa is not None and sa.is_accept
        assert sb is not None and sb.is_accept

    def test_concat_dfa(self):
        ast = parse_pattern('"a" "b"')
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        sa = dfa.transition(dfa.start, "a")
        assert sa is not None and not sa.is_accept
        sb = dfa.transition(sa, "b")
        assert sb is not None and sb.is_accept

    def test_star_dfa(self):
        ast = parse_pattern('"a"*')
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        # Start state should be accepting (matches empty string)
        assert dfa.start.is_accept

    def test_dfa_is_deterministic(self):
        ast = parse_pattern('(letra|digito)+')
        nfa = ast_to_nfa(ast)
        dfa = nfa_to_dfa(nfa)
        # Each state should have at most one transition per symbol
        for state in dfa.states:
            for sym in dfa.alphabet:
                # transitions dict maps symbol to single state (not set)
                if sym in state.transitions:
                    assert isinstance(state.transitions[sym], type(state))
