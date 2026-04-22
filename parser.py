from grammar import Item, get_start_item

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
    return list(grammar.nonTerminals) + list(grammar.terminals)

def build_dfa(grammar):
    states = []
    transitions = {}

    start_item = get_start_item(grammar)
    start_state = frozenset(closure({start_item}, grammar))

    states.append(start_state)

    i = 0
    while i < len(states):
        state = states[i]

        for symbol in get_all_symbols(grammar):
            next_state = frozenset(goto(state, symbol, grammar))

            if not next_state:
                continue

            if next_state not in states:
                states.append(next_state)

            next_index = states.index(next_state)
            transitions[(i, symbol)] = next_index

        i += 1

    return states, transitions

def print_state(state, index):
    print(f"\nI{index}:")
    for item in sorted(state, key=lambda x: (x.prod_num, x.dot)):
        print(item)


def print_dfa(states, transitions):
    for i, state in enumerate(states):
        print_state(state, i)

    print("\nTransitions:")
    for (from_state, symbol), to_state in sorted(transitions.items()):
        print(f"I{from_state} -- {symbol} --> I{to_state}")

def build_parsing_table(grammar, states, transitions):
    action = {}
    goto_table = {}
    conflicts = []

    terminals = list(grammar.terminals) + ["$"]

    for (state_index, symbol), next_state in transitions.items():
        if symbol in grammar.terminals:
            key = (state_index, symbol)
            value = f"s{next_state}"

            if key in action and action[key] != value:
                conflicts.append((key, action[key], value))
            action[key] = value

        elif symbol in grammar.nonTerminals:
            goto_table[(state_index, symbol)] = next_state

    for i, state in enumerate(states):
        for item in state:
            if item.is_complete():
                if item.lhs == grammar.augmented_start_symbol:
                    key = (i, "$")
                    value = "acc"
                    if key in action and action[key] != value:
                        conflicts.append((key, action[key], value))
                    action[key] = value
                else:
                    value = f"r{item.prod_num}"
                    for terminal in terminals:
                        key = (i, terminal)
                        if key in action and action[key] != value:
                            conflicts.append((key, action[key], value))
                        action[key] = value

    return action, goto_table, conflicts

def print_parsing_table(grammar, action, goto_table):
    terminals = sorted(grammar.terminals) + ["$"]
    nonterminals = sorted(grammar.nonTerminals - {grammar.augmented_start_symbol})

    print("\nACTION TABLE:")
    for state, symbol in sorted(action):
        print(f"ACTION[{state}, {symbol}] = {action[(state, symbol)]}")

    print("\nGOTO TABLE:")
    for state, symbol in sorted(goto_table):
        print(f"GOTO[{state}, {symbol}] = {goto_table[(state, symbol)]}")

def parse_string(grammar, action, goto_table, input_text):
    tokens = input_text.split()
    tokens.append("$")

    stack = [0]
    steps = []

    step_no = 1

    while True:
        state = stack[-1]
        current = tokens[0]

        act = action.get((state, current), "")

        steps.append({
            "step": step_no,
            "stack": " ".join(map(str, stack)),
            "input": " ".join(tokens),
            "action": act if act else "error"
        })

        if not act:
            return False, steps

        if act == "acc":
            return True, steps

        if act.startswith("s"):
            next_state = int(act[1:])
            stack.append(current)
            stack.append(next_state)
            tokens.pop(0)

        elif act.startswith("r"):
            prod_num = int(act[1:])
            prod = grammar.productions[prod_num]

            pop_count = 2 * len(prod.rhs)
            for _ in range(pop_count):
                stack.pop()

            top_state = stack[-1]
            stack.append(prod.lhs)

            next_state = goto_table.get((top_state, prod.lhs))
            if next_state is None:
                steps.append({
                    "step": step_no + 1,
                    "stack": " ".join(map(str, stack)),
                    "input": " ".join(tokens),
                    "action": "error"
                })
                return False, steps

            stack.append(next_state)

        else:
            return False, steps

        step_no += 1