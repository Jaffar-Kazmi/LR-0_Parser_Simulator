import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


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

        # Build UI inside scrollable_frame
        self.build_ui()

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def build_ui(self):
        parent = self.scrollable_frame   # 👈 IMPORTANT

        grammar_frame = tk.LabelFrame(parent, text="Grammar")
        grammar_frame.pack(fill='x', padx=10, pady=10)

        self.grammar_text = ScrolledText(grammar_frame, height=8)
        self.grammar_text.pack(fill='x', padx=5, pady=5)

        button_frame = tk.Frame(grammar_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        self.build_button = tk.Button(button_frame, text="Build DFA & Table")
        self.build_button.pack(side='left', padx=5)

        output_frame = tk.LabelFrame(parent, text="Output")
        output_frame.pack(fill='x', padx=10, pady=10)

        self.output_text = ScrolledText(output_frame)
        self.output_text.pack(fill='x', padx=5, pady=5)

        input_frame = tk.LabelFrame(parent, text="Input String")
        input_frame.pack(fill='x', padx=10, pady=10)

        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)

        self.parse_button = tk.Button(input_frame, text="Parse String")
        self.parse_button.pack(side="left", padx=10, pady=10)

        result_frame = tk.LabelFrame(parent, text="Result")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_label = tk.Label(result_frame, text="Result will appear here", font=("Arial", 12, "bold"))
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