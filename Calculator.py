import sympy as sp
from tkinter import *
import tkinter as tk
import math as mp
from fractions import Fraction
import numpy as np

class Calculator:
    def __init__(self):
        self.calculator = Tk()
        self.calculator.title("Calculator")
        self.calculator.geometry("295x445")
        self.calculator.configure(bg="grey14")
        self.calculator.resizable(False, False)

        self.shift_mode = False
        self.angle_mode = "rad"
        self.history = []
        self.history_window = None

        self.List = [["C", "(", ")", "DEL"], ["x²", "√x", "eˣ", "/"], ["7", "8", "9", "×"], ["4", "5", "6", "-"], ["1", "2", "3", "+"], [".", "0", "^", "="]]
        self.top = ["shift", "+/-", "S⇔D", "history"]
        self.List_shift = [["sin(x)", "cos(x)", "tan(x)", "DEL"], ["x!", "log(x)", "ln(x)", "Abs"], ["7", "8", "9", "deg"], ["4", "5", "6", "rad"], ["1", "2", "3", "grad"], ["π", "0", "^", "="]]

        self.display = Display(self)
        self.history_manager = History(self)
        self.setup_buttons()

        self.calculator.bind("<F11>", self.disable_fullscreen)
        self.calculator.mainloop()
    def setup_buttons(self):
        self.buttons = []
        for i in range(4):
            row = []
            for j in range(6):
                button_name = self.List[j][i]
                bg_color = "grey33" if button_name.isdigit() else "gray23"
                button = tk.Button(self.calculator, text=button_name, height="3", width="9",
                                   command=lambda btn=button_name: self.button_click(btn), bg=bg_color, fg="white",
                                   highlightthickness=0, bd=0)
                button.grid(row=j + 2, column=i, padx=1, pady=3)
                row.append(button)
            self.buttons.append(row)

        self.top_row = [tk.Button(self.calculator, text=button_name, height="1", width="9", command=lambda btn=button_name: self.button_click(btn), bg="gray14", fg="white", highlightthickness=0, bd=0) for button_name in self.top]

        for k, button in enumerate(self.top_row):
            button.grid(row=1, column=k, padx=1, pady=3)

        self.shift_button = tk.Button(self.calculator, text="shift", height="1", width="9", command=lambda: self.button_click("shift"), bg="gray14", fg="white", highlightthickness=0, bd=0)
        self.shift_button.grid(row=1, column=0, columnspan=1, padx=1, pady=3)

        self.angle_buttons = {}
        for mode, column in zip(["deg", "rad", "grad"], range(4, 7)):
            self.angle_buttons[mode] = tk.Button(self.calculator, text=mode, height="3", width="9", command=lambda m=mode: self.button_click(m), bg="gray23", fg="white", highlightthickness=0, bd=0)
            self.angle_buttons[mode].grid(row=column, column=3, padx=1, pady=3)
            self.angle_buttons[mode].grid_remove()
    def disable_fullscreen(self, event):
        if (event.state & 0x100):
            return "break"
    def button_click(self, character):
        pos = self.display.txt.index(INSERT)
        actions = {
            "DEL": lambda: pos != '1.0' and self.display.txt.delete(f"{pos} - 1 chars", pos),
            "C": lambda: self.display.txt.delete("1.0", END),
            "x²": lambda: self.display.txt.insert(pos, "^2"),
            "eˣ": lambda: (self.display.txt.insert(pos, "exp()"), self.display.txt.mark_set(INSERT, f"{pos} + 4 chars")),
            "√x": lambda: (self.display.txt.insert(pos, "√()"), self.display.txt.mark_set(INSERT, f"{pos} + 2 chars")),
            "=": self.calculate,
            "S⇔D": self.s_and_d,
            "+/-": self.change_positive_negative,
            "shift": self.toggle_shift,
            "Abs": self.absolut,
            "ln(x)": lambda: (self.display.txt.insert(pos, "ln()"), self.display.txt.mark_set(INSERT, f"{pos} + 3 chars")),
            "log(x)": lambda: (self.display.txt.insert(pos, "log()"), self.display.txt.mark_set(INSERT, f"{pos} + 4 chars")),
            "x!": lambda: (self.display.txt.insert(pos, "()!"), self.display.txt.mark_set(INSERT, f"{pos} + 1 chars")),
            "sin(x)": lambda: (self.display.txt.insert(pos, "sin()"), self.display.txt.mark_set(INSERT, f"{pos} + 4 chars")),
            "cos(x)": lambda: (self.display.txt.insert(pos, "cos()"), self.display.txt.mark_set(INSERT, f"{pos} + 4 chars")),
            "tan(x)": lambda: (self.display.txt.insert(pos, "tan()"), self.display.txt.mark_set(INSERT, f"{pos} + 4 chars")),
            "rad": lambda: self.set_angle_mode("rad"),
            "deg": lambda: self.set_angle_mode("deg"),
            "grad": lambda: self.set_angle_mode("grad"),
            "history": self.history_manager.show_history
        }
        actions.get(character, lambda: self.display.txt.insert(pos, character))()
        self.update_buttons()
    def calculate(self):
        try:
            expression = self.display.txt.get("1.0", END).strip().replace("×", "*").replace("π", "pi").replace("^", "**").replace("sp.exp", "np.exp").replace("√", "sqrt")

            # Handle factorials
            while '!' in expression:
                idx = expression.index('!')
                num_end = idx - 1
                if expression[num_end] == ')':
                    num_start = expression.rindex('(', 0, num_end)
                    num = expression[num_start + 1:num_end]
                    fact_result = str(mp.factorial(int(num)))
                    expression = expression[:num_start] + fact_result + expression[idx + 1:]
                else:
                    num_start = num_end
                    while num_start >= 0 and (expression[num_start].isdigit() or expression[num_start] == '.'):
                        num_start -= 1
                    num = expression[num_start + 1:idx]
                    fact_result = str(mp.factorial(int(num)))
                    expression = expression[:num_start + 1] + fact_result + expression[idx + 1:]

            if not expression or '=' in expression or expression.count('(') != expression.count(')'):
                raise ValueError("Invalid expression")
            expression = self.convert_angles(expression)
            result = sp.sympify(expression).evalf()
            result_str = format(result, '.12f').rstrip('0').rstrip('.')

            self.history.append(f"{expression} = {result_str}")
            if len(self.history) > 5:
                self.history.pop(0)

            self.display.txt.delete("1.0", "end")
            self.display.txt.insert("1.0", result_str)

        except Exception:
            self.display.txt.delete("1.0", "end")
            self.display.txt.insert("1.0", "Error")
    def toggle_shift(self):
        self.shift_mode = not self.shift_mode
        self.update_buttons()
    def update_buttons(self):
        button_list = self.List_shift if self.shift_mode else self.List
        self.shift_button.config(fg="green" if self.shift_mode else "white")

        for i in range(4):
            for j in range(6):
                button_text = button_list[j][i]
                self.buttons[i][j].config(text=button_text, command=lambda btn=button_text: self.button_click(btn))

        for mode in ["deg", "rad", "grad"]:
            if self.shift_mode:
                self.angle_buttons[mode].grid()
            else:
                self.angle_buttons[mode].grid_remove()
            self.update_angle_button_color(mode)
    def update_angle_button_color(self, mode):
        self.angle_buttons[mode].config(fg="green" if mode == self.angle_mode else "White")
    def set_angle_mode(self, mode):
        self.angle_mode = mode
        self.update_buttons()
    def convert_angles(self, expression):
        if self.angle_mode in ["grad", "deg"]:
            factor = {"grad": "pi/200", "deg": "pi/180"}[self.angle_mode]
            expression = expression.replace("sin(", f"sin({factor} * ").replace("cos(", f"cos({factor} * ").replace("tan(", f"tan({factor} * ")
        return expression
    def s_and_d(self):
        try:
            current_text = self.display.txt.get("1.0", END).strip()
            result = float(Fraction(current_text)) if "/" in current_text else Fraction(current_text).limit_denominator()
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", "{:.15g}".format(result) if isinstance(result, float) else str(result))
        except ValueError:
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", "Invalid input")
    def absolut(self):
        current_text = self.display.txt.get("1.0", END).strip()
        try:
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", str(abs(float(current_text))))
        except ValueError:
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", "Invalid input")
    def change_positive_negative(self):
        current_text = self.display.txt.get("1.0", END).strip()
        try:
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", str(-float(current_text)))
        except ValueError:
            self.display.txt.delete("1.0", END)
            self.display.txt.insert("1.0", "Invalid input")

class Display:
    def __init__(self, calculator):
        self.calculator = calculator.calculator
        self.txt = tk.Text(self.calculator, height=1.5, width=17, font=("Courier New", 21), bg="grey14", fg="white", highlightthickness=0, bd=0)
        self.txt.grid(row=0, column=0, columnspan=4, padx=1, pady=7)
        self.txt.configure(insertbackground="white")
        self.txt.tag_configure("center", justify="center")
        self.txt.bind("<Key>", self.on_key_press)

        self.context_menu = tk.Menu(self.calculator, tearoff=0)
        self.context_menu.add_command(label="copy", command=self.copy_text)
        self.context_menu.add_command(label="insert", command=self.paste_text)
        self.txt.bind("<Button-3>", self.show_context_menu)
    def copy_text(self):
        self.txt.clipboard_clear(),
        self.txt.clipboard_append(self.txt.get(tk.SEL_FIRST, tk.SEL_LAST))
    def paste_text(self):
        self.txt.insert(tk.INSERT, self.txt.clipboard_get())
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    def on_key_press(self, event):
        key_pressed = event.keysym
        if key_pressed == "BackSpace":
            self.calculator.button_click("DEL")
        elif key_pressed.isdigit() or key_pressed in "e/+-^()π.!*":
            self.calculator.button_click(key_pressed.replace("*", "×"))
        return "break"

class History:
    def __init__(self, calculator):
        self.calculator = calculator
        self.history_window = None
    def show_history(self):
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()
            self.toggle_history_button_text(False)
            return

        self.history_window = Toplevel(self.calculator.calculator)
        self.history_window.geometry("292x300+0+205")
        self.history_window.overrideredirect(True)
        self.history_window.configure(bg="grey14")

        Label(self.history_window, text="History", font=("Courier New", 21, "underline"), bg="grey14", fg="white").pack(pady=5)

        history_text = Text(self.history_window, height=11, width=29, font=("Courier New", 15), bg="grey14", fg="white", highlightthickness=0, bd=0)
        history_text.pack(pady=5)
        history_text.insert(END, "\n\n".join(self.calculator.history))

        history_context_menu = Menu(self.history_window, tearoff=0)
        history_context_menu.add_command(label="Copy", command=lambda: self.history_window.clipboard_append(history_text.get(tk.SEL_FIRST, tk.SEL_LAST)))
        history_text.bind("<Button-3>", lambda event: history_context_menu.post(event.x_root, event.y_root))

        self.update_history_window_position()
        self.calculator.calculator.bind("<Configure>", lambda e: self.update_history_window_position())
        self.toggle_history_button_text(True)
    def toggle_history_button_text(self, opened):
        self.calculator.top_row[-1].config(text="History")
    def update_history_window_position(self):
        if self.history_window and isinstance(self.history_window, tk.Toplevel) and self.history_window.winfo_exists():
            x, y = self.calculator.calculator.winfo_x(), self.calculator.calculator.winfo_y()
            self.history_window.geometry(f"292x300+{x + 8}+{y + 175}")

if __name__ == "__main__":
    Calculator()
