from grammar import parse_grammar, augment_grammar
from parser import build_dfa, build_parsing_table, parse_string

sample_grammar = """
S -> C C
C -> c C | d
"""
grammar = parse_grammar(sample_grammar)
grammar = augment_grammar(grammar)


states, transitions = build_dfa(grammar)
action, goto_table, _ = build_parsing_table(grammar, states, transitions)

accepted, steps = parse_string(grammar, action, goto_table, "d d")

