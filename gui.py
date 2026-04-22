import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from grammar import parse_grammar, augment_grammar
from parser import build_dfa, build_parsing_table, parse_string


class LR0App:
    def __init__(self, root):
        self.root = root
        self.root.title("LR(0) Parser")
        self.root.geometry("1000x700")

        self.canvas = tk.Canvas(root)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.build_ui()

        self.grammar = None
        self.states = None
        self.transitions = None
        self.action_table = None
        self.goto_table = None

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def build_ui(self):
        parent = self.scrollable_frame

        grammar_frame = tk.LabelFrame(parent, text="Grammar")
        grammar_frame.pack(fill="x", padx=10, pady=10)

        self.grammar_text = ScrolledText(grammar_frame, height=8)
        self.grammar_text.pack(fill="x", padx=5, pady=5)

        button_frame = tk.Frame(grammar_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.build_button = tk.Button(
            button_frame,
            text="Build DFA & Table",
            command=self.build_parser
        )
        self.build_button.pack(side="left", padx=5)

        output_frame = tk.LabelFrame(parent, text="Output")
        output_frame.pack(fill="x", padx=10, pady=10)

        self.output_text = ScrolledText(output_frame, height=15)
        self.output_text.pack(fill="x", padx=5, pady=5)

        input_frame = tk.LabelFrame(parent, text="Input String")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.parse_button = tk.Button(
            input_frame,
            text="Parse String",
            command=self.parse_input
        )
        self.parse_button.pack(side="left", padx=10, pady=10)

        result_frame = tk.LabelFrame(parent, text="Result")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_label = tk.Label(
            result_frame,
            text="Result will appear here",
            font=("Arial", 12, "bold")
        )
        self.result_label.pack(anchor="w", padx=10, pady=10)

        columns = ("Step", "Stack", "Input", "Action")
        self.steps_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.steps_tree.heading(col, text=col)
            self.steps_tree.column(col, width=150)

        self.steps_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def build_parser(self):
        try:
            grammar_text = self.grammar_text.get("1.0", tk.END).strip()
            if not grammar_text:
                messagebox.showerror("Error", "Please enter a grammar.")
                return

            self.grammar = parse_grammar(grammar_text)
            self.grammar = augment_grammar(self.grammar)

            self.states, self.transitions = build_dfa(self.grammar)
            self.action_table, self.goto_table, conflicts = build_parsing_table(
                self.grammar,
                self.states,
                self.transitions
            )

            self.output_text.delete("1.0", tk.END)

            self.output_text.insert(tk.END, "DFA STATES:\n\n")
            for i, state in enumerate(self.states):
                self.output_text.insert(tk.END, f"I{i}:\n")
                for item in sorted(state, key=lambda x: (x.prod_num, x.dot)):
                    self.output_text.insert(tk.END, f"  {item}\n")
                self.output_text.insert(tk.END, "\n")

            self.output_text.insert(tk.END, "TRANSITIONS:\n")
            for (from_state, symbol), to_state in sorted(self.transitions.items()):
                self.output_text.insert(tk.END, f"I{from_state} -- {symbol} --> I{to_state}\n")

            self.output_text.insert(tk.END, "\nACTION TABLE:\n")
            for key in sorted(self.action_table):
                self.output_text.insert(tk.END, f"ACTION{key} = {self.action_table[key]}\n")

            self.output_text.insert(tk.END, "\nGOTO TABLE:\n")
            for key in sorted(self.goto_table):
                self.output_text.insert(tk.END, f"GOTO{key} = {self.goto_table[key]}\n")

            self.output_text.insert(tk.END, "\nCONFLICTS:\n")
            if conflicts:
                for conflict in conflicts:
                    self.output_text.insert(tk.END, f"{conflict}\n")
                self.result_label.config(text="Grammar is NOT LR(0)", fg="red")
            else:
                self.output_text.insert(tk.END, "No conflicts. Grammar is LR(0).\n")
                self.result_label.config(text="Grammar built successfully", fg="green")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def parse_input(self):
        try:
            if self.grammar is None or self.action_table is None or self.goto_table is None:
                messagebox.showerror("Error", "Build the parser first.")
                return

            input_text = self.input_entry.get().strip()
            if not input_text:
                messagebox.showerror("Error", "Please enter an input string.")
                return

            accepted, steps = parse_string(
                self.grammar,
                self.action_table,
                self.goto_table,
                input_text
            )

            for item in self.steps_tree.get_children():
                self.steps_tree.delete(item)

            for row in steps:
                self.steps_tree.insert("", tk.END, values=(
                    row["step"],
                    row["stack"],
                    row["input"],
                    row["action"]
                ))

            if accepted:
                self.result_label.config(text="ACCEPTED", fg="green")
            else:
                self.result_label.config(text="REJECTED", fg="red")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LR0App(root)
    root.mainloop()