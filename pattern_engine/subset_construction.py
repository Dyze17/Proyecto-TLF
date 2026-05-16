"""
Subset construction — converts an NFA into a DFA.

Algorithm
---------
1. Compute ε-closure of the NFA start state → initial DFA state.
2. For each unmarked DFA state and each symbol in the alphabet,
   compute the ε-closure of the set of states reachable via that
   symbol.  If the resulting set is new, create a new DFA state.
3. Repeat until no new DFA states are created.
"""

from __future__ import annotations
from typing import Dict, FrozenSet, Set

from .nfa import NFA, NFAState
from .dfa import DFA, DFAState


def _epsilon_closure(states: Set[NFAState]) -> FrozenSet[int]:
    """Compute ε-closure of a set of NFA states (returns frozenset of ids)."""
    stack = list(states)
    closure: Set[int] = {s.id for s in states}
    state_map: Dict[int, NFAState] = {s.id: s for s in states}

    while stack:
        s = stack.pop()
        for t in s.epsilon_transitions:
            if t.id not in closure:
                closure.add(t.id)
                state_map[t.id] = t
                stack.append(t)

    return frozenset(closure), state_map


def _epsilon_closure_full(states: Set[NFAState]) -> tuple[FrozenSet[int], Dict[int, NFAState]]:
    """Like _epsilon_closure but also returns the id→state mapping."""
    stack = list(states)
    closure: Set[int] = {s.id for s in states}
    state_map: Dict[int, NFAState] = {s.id: s for s in states}

    while stack:
        s = stack.pop()
        for t in s.epsilon_transitions:
            if t.id not in closure:
                closure.add(t.id)
                state_map[t.id] = t
                stack.append(t)

    return frozenset(closure), state_map


def _move(
    state_ids: FrozenSet[int],
    symbol: str,
    id_to_state: Dict[int, NFAState],
) -> Set[NFAState]:
    """Compute move(T, a) — all states reachable from *state_ids* via *symbol*."""
    result: Set[NFAState] = set()
    for sid in state_ids:
        state = id_to_state.get(sid)
        if state is None:
            continue
        for target in state.transitions.get(symbol, set()):
            result.add(target)
    return result


def nfa_to_dfa(nfa: NFA) -> DFA:
    """Convert *nfa* into an equivalent DFA via subset construction."""

    # Reset DFA state counter
    DFAState._counter = 0

    # Collect all NFA states and build a global id→state map
    all_nfa_states = nfa.states
    global_map: Dict[int, NFAState] = {s.id: s for s in all_nfa_states}
    accept_id = nfa.accept.id

    # Compute alphabet from the NFA
    alphabet: Set[str] = nfa.alphabet()

    # Initial DFA state = ε-closure({start})
    start_ids, start_map = _epsilon_closure_full({nfa.start})
    global_map.update(start_map)

    start_is_accept = accept_id in start_ids
    dfa_start = DFAState(start_ids, is_accept=start_is_accept)

    # Map frozenset of NFA-state-ids → DFA state
    dfa_state_map: Dict[FrozenSet[int], DFAState] = {start_ids: dfa_start}
    unmarked: list[FrozenSet[int]] = [start_ids]

    dfa_states: Set[DFAState] = {dfa_start}
    accept_states: Set[DFAState] = set()
    if start_is_accept:
        accept_states.add(dfa_start)

    while unmarked:
        current_ids = unmarked.pop()
        current_dfa = dfa_state_map[current_ids]

        for symbol in alphabet:
            target_nfa_states = _move(current_ids, symbol, global_map)
            if not target_nfa_states:
                continue

            target_ids, target_map = _epsilon_closure_full(target_nfa_states)
            global_map.update(target_map)

            if target_ids not in dfa_state_map:
                is_accept = accept_id in target_ids
                new_dfa = DFAState(target_ids, is_accept=is_accept)
                dfa_state_map[target_ids] = new_dfa
                dfa_states.add(new_dfa)
                unmarked.append(target_ids)
                if is_accept:
                    accept_states.add(new_dfa)

            current_dfa.add_transition(symbol, dfa_state_map[target_ids])

    return DFA(
        start=dfa_start,
        states=dfa_states,
        accept_states=accept_states,
        alphabet=alphabet,
    )
