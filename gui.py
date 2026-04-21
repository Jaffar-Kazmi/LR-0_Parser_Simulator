import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class LR0App:
    def __init__(self, root):
        self.root = root
        self.root.title("LR(0) Parser")
        self.root.geometry("1000x700")

        self.build_ui()

    def build_ui(self):
        # Top frame - grammar
        grammar_frame = ttk.LabelFrame(self.root, text="Grammar")
        grammar_frame.pack(fill="x", padx=10, pady=10)

        self.grammar_text = ScrolledText(grammar_frame, height=8)
        self.grammar_text.pack(fill="x", padx=10, pady=10)

        button_frame = ttk.Frame(grammar_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.build_button = ttk.Button(button_frame, text="Build DFA & Table")
        self.build_button.pack(side="left", padx=5)

        self.load_button = ttk.Button(button_frame, text="Load Example")
        self.load_button.pack(side="left", padx=5)

        # Middle frame - output
        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_text = ScrolledText(output_frame, height=15)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

        # String input frame
        input_frame = ttk.LabelFrame(self.root, text="String Input")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.parse_button = ttk.Button(input_frame, text="Parse String")
        self.parse_button.pack(side="left", padx=10, pady=10)

        # Result frame
        result_frame = ttk.LabelFrame(self.root, text="Result")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_label = ttk.Label(result_frame, text="Result will appear here", font=("Arial", 12, "bold"))
        self.result_label.pack(anchor="w", padx=10, pady=10)

        columns = ("Step", "Stack", "Input", "Action")
        self.steps_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.steps_tree.heading(col, text=col)
            self.steps_tree.column(col, width=150)

        self.steps_tree.pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = LR0App(root)
    root.mainloop()