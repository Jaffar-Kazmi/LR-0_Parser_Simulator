from dataclasses import dataclass, field

@dataclass(frozen=True)
class Production:
    number: int
    lhs: str
    rhs: tuple[str, ...]

    def __str__(self):
        rhs_text = ' '.join(self.rhs) if self.rhs else 'ε'
        return f"{self.number}. {self.lhs} -> {rhs_text}"

@dataclass(frozen=True)
class Item:
    prod_num: int
    lhs: str
    rhs: tuple[str, ...]
    dot: int

    def next_symbol(self):
        if self.dot < len(self.rhs):
            return self.rhs[self.dot]
        return None
    
    def is_complete(self):
        return self.dot >= len(self.rhs)
    
    def move_dot(self):
        if self.dot < len(self.rhs):
            return Item(self.prod_num, self.lhs, self.rhs, self.dot + 1)
        return self  
    
    def __str__(self):
        rhs = list(self.rhs)
        rhs.insert(self.dot, '•')
        return f"{self.prod_num}. {self.lhs} -> {' '.join(rhs)}"

@dataclass
class Grammar:
    start_symbol: str = ""
    augmented_start_symbol: str = ""
    productions: list[Production] = field(default_factory=list)
    nonTerminals: set[str] = field(default_factory=set)
    terminals: set[str] = field(default_factory=set)

    def __str__(self):
        lines = [
            f"Start Symbol: {self.start_symbol}",
            f"Non-terminals: {sorted(self.nonTerminals)}",
            f"Terminals: {sorted(self.terminals)}",
            "Productions:"
        ]
        lines.extend(str(p) for p in self.productions)
        return '\n'.join(lines)

def parse_grammar(text: str):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        raise ValueError("Input grammar is empty.")
    
    raw_rules = []
    nonTerminals = set()
    terminals = set()

    for line in lines:
        if '->' not in line:
            raise ValueError(f"Invalid production rule: '{line}'. Expected '->' separator.")
        lhs, rhs = line.split('->', 1)
        if not lhs.strip():
            raise ValueError(f"Invalid production rule: '{line}'. Left-hand side cannot be empty.")
        nonTerminals.add(lhs.strip())
        raw_rules.append((lhs.strip(), rhs.strip()))

    productions = []
    prod_number = 0

    for lhs, rhs_part in raw_rules:
        alternatives = [alt.strip() for alt in rhs_part.split("|")]
        for alt in alternatives:
            if alt in ("", "ε", "epsilon"):
                rhs = tuple()
            else:
                rhs = tuple(alt.split())
            productions.append(Production(prod_number, lhs, rhs))
            prod_number += 1

    for prod in productions:
        for symbol in prod.rhs:
            if symbol not in nonTerminals:
                terminals.add(symbol)     

    grammar = Grammar(
        start_symbol=productions[0].lhs,
        productions=productions,
        nonTerminals=nonTerminals,
        terminals=terminals
    )

    return grammar   

def augment_grammar(grammar):
    new_start = grammar.start_symbol + "'"

    while new_start in grammar.nonTerminals:
        new_start += "'"

    new_productions = [Production(0, new_start, (grammar.start_symbol,))]

    for i, prod in enumerate(grammar.productions, start=1):
        new_productions.append(Production(i, prod.lhs, prod.rhs))

    return Grammar(
        start_symbol=grammar.start_symbol,
        augmented_start_symbol=new_start,
        productions=new_productions,
        nonTerminals=grammar.nonTerminals.union({new_start}),
        terminals=grammar.terminals
    )

def get_start_item(grammar):
    start_prod = grammar.productions[0]
    return Item(start_prod.number, start_prod.lhs, start_prod.rhs, 0)

def closure(items, grammar):
    result = set(items)

    changed = True
    while changed:
        changed = False

        for item in list(result):
            symbol = item.next_symbol()

            if symbol in grammar.nonTerminals:
                for prod in grammar.productions:
                    if prod.lhs == symbol:
                        new_item = Item(prod.number, prod.lhs, prod.rhs, 0)
                        if new_item not in result:
                            result.add(new_item)
                            changed = True

    return result

def print_items(items, title="Items"):
    print(f"\n{title}:")
    for item in sorted(items, key=lambda x: (x.prod_num, x.dot)):
        print(item)

def goto(items, symbol, grammar):
    moved = set()

    for item in items:
        if item.next_symbol() == symbol:
            moved.add(item.move_dot())

    if not moved:
        return set()

    return closure(moved, grammar)

def get_all_symbols(grammar):
    return list(grammar.nonterminals) + list(grammar.terminals)

if __name__ == "__main__":
    sample_grammar = """
    S -> C C
    C -> c C | d
    """

    grammar = parse_grammar(sample_grammar)
    grammar = augment_grammar(grammar)

    start_item = get_start_item(grammar)
    state0 = closure({start_item}, grammar)

    print_items(state0, "I0")

    state_on_S = goto(state0, "S", grammar)
    print_items(state_on_S, "goto(I0, S)")

    state_on_C = goto(state0, "C", grammar)
    print_items(state_on_C, "goto(I0, C)")

    state_on_c = goto(state0, "c", grammar)
    print_items(state_on_c, "goto(I0, c)")

    state_on_d = goto(state0, "d", grammar)
    print_items(state_on_d, "goto(I0, d)")

# p1 = Production(1, 'S', ('A', 'B'))
# print(p1)  # Output: 1. S -> A B
# p2 = Production(2, 'A', ('a',))
# print(p2)  # Output: 2. A -> a
# p3 = Production(3, 'B', ())
# print(p3)  # Output: 3. B -> ε

# g = Grammar(
#     start_symbol='S',
#     productions=[p1, p2, p3],
#     nonTerminals={'S', 'A', 'B'},
#     terminals={'a'}
# )
# print(g)