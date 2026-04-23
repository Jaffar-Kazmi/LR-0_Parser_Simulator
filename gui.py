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

        self.grammar = None
        self.states = None
        self.transitions = None
        self.action_table = None
        self.goto_table = None
        self.state_positions = {}
        self.state_circles = {}

        self.build_ui()

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

        dfa_frame = tk.LabelFrame(parent, text="DFA Diagram")
        dfa_frame.pack(fill="both", expand=True, padx=10, pady=10)

        dfa_canvas_frame = tk.Frame(dfa_frame)
        dfa_canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.dfa_canvas = tk.Canvas(dfa_canvas_frame, bg="white", height=750)
        self.dfa_canvas.grid(row=0, column=0, sticky="nsew")

        self.dfa_vscroll = tk.Scrollbar(dfa_canvas_frame, orient="vertical", command=self.dfa_canvas.yview)
        self.dfa_vscroll.grid(row=0, column=1, sticky="ns")

        self.dfa_hscroll = tk.Scrollbar(dfa_canvas_frame, orient="horizontal", command=self.dfa_canvas.xview)
        self.dfa_hscroll.grid(row=1, column=0, sticky="ew")

        self.dfa_canvas.configure(
            yscrollcommand=self.dfa_vscroll.set,
            xscrollcommand=self.dfa_hscroll.set
        )

        dfa_canvas_frame.grid_rowconfigure(0, weight=1)
        dfa_canvas_frame.grid_columnconfigure(0, weight=1)
        
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

    def draw_dfa(self):
        self.dfa_canvas.delete("all")

        if not self.states:
            return

        self.state_positions = {}
        self.state_boxes = {}

        start_x = 60
        start_y = 60
        gap_x = 280
        gap_y = 220

        box_w = 240
        box_h = 160

        for i in range(len(self.states)):
            row = i // 3
            col = i % 3
            x = start_x + col * gap_x
            y = start_y + row * gap_y
            self.state_positions[i] = (x, y)

        for (from_state, symbol), to_state in self.transitions.items():
            x1, y1 = self.state_positions[from_state]
            x2, y2 = self.state_positions[to_state]
        
            if from_state == to_state:
                self.dfa_canvas.create_arc(
                    x1 + 80, y1 - 30, x1 + 180, y1 + 40,
                    start=0, extent=300, style="arc", width=2
                )
                self.dfa_canvas.create_text(x1 + 130, y1 - 20, text=symbol, fill="blue")
            else:
                sx, sy = self.get_box_edge_point(x1, y1, x2, y2, box_w, box_h)
                tx, ty = self.get_box_edge_point(x2, y2, x1, y1, box_w, box_h)
        
                self.dfa_canvas.create_line(
                    sx, sy, tx, ty,
                    arrow=tk.LAST,
                    width=2
                )
        
                mx = (sx + tx) / 2
                my = (sy + ty) / 2
                self.dfa_canvas.create_rectangle(mx - 12, my - 10, mx + 12, my + 10, fill="white", outline="")
                self.dfa_canvas.create_text(mx, my, text=symbol, fill="blue")

        for i, state in enumerate(self.states):
            x, y = self.state_positions[i]

            rect = self.dfa_canvas.create_rectangle(
                x, y, x + box_w, y + box_h,
                outline="black",
                width=2,
                fill="lightgray"
            )

            self.dfa_canvas.create_text(
                x + 10, y + 10,
                text=f"I{i}",
                anchor="nw",
                font=("Arial", 11, "bold")
            )

            items = sorted(state, key=lambda it: (it.prod_num, it.dot))
            text = "\n".join(str(item) for item in items)

            self.dfa_canvas.create_text(
                x + 10, y + 35,
                text=text,
                anchor="nw",
                font=("Consolas", 9),
                justify="left"
            )

            self.state_circles[i] = rect

    def highlight_state(self, state_index):
        for circle in self.state_circles.values():
            self.dfa_canvas.itemconfig(circle, fill="lightgray")

        if state_index in self.state_circles:
            self.dfa_canvas.itemconfig(self.state_circles[state_index], fill="yellow")

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

            self.draw_dfa()

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

            if steps:
                # simple visual sync: highlight last seen state if available later
                pass

            if accepted:
                self.result_label.config(text="ACCEPTED", fg="green")
            else:
                self.result_label.config(text="REJECTED", fg="red")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_box_edge_point(self, x1, y1, x2, y2, box_w, box_h):
        cx1 = x1 + box_w / 2
        cy1 = y1 + box_h / 2
        cx2 = x2 + box_w / 2
        cy2 = y2 + box_h / 2

        dx = cx2 - cx1
        dy = cy2 - cy1

        if dx == 0 and dy == 0:
            return cx1, cy1

        if abs(dx) * box_h > abs(dy) * box_w:
            if dx > 0:
                px = x1 + box_w
                py = cy1 + dy * (box_w / 2) / abs(dx)
            else:
                px = x1
                py = cy1 - dy * (box_w / 2) / abs(dx)
        else:
            if dy > 0:
                py = y1 + box_h
                px = cx1 + dx * (box_h / 2) / abs(dy)
            else:
                py = y1
                px = cx1 - dx * (box_h / 2) / abs(dy)

        return px, py


if __name__ == "__main__":
    root = tk.Tk()
    app = LR0App(root)
    root.mainloop()