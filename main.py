import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import numpy as np
from scipy.optimize import linprog
from ttkbootstrap import Style

def solve_lp():
    try:
        num_vars = int(num_vars_entry.get())
        num_constraints = int(num_constraints_entry.get())
    except ValueError:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Invalid input. Please enter valid numbers for variables and constraints.")
        return

    optimization_goal = optimization_var.get()
    try:
        objective = []
        for i in range(num_vars):
            coeff_str = objective_entries[i].get()
            coeff = float(coeff_str)
            objective.append(coeff)

        if optimization_goal == "Maximize":
            objective = [-x for x in objective]
    except ValueError:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Objective function error")
        return

    lhs_constraints = []
    rhs_constraints = []
    inequality_signs = []

    try:
        for row in constraint_rows:
            lhs = [float(e.get()) for e in row.entries[:-1]]
            sign = row.inequality_var.get()  # Corrected here
            rhs = float(row.entries[-1].get())
            lhs_constraints.append(lhs)
            rhs_constraints.append(rhs)
            inequality_signs.append(sign)
    except ValueError:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Constraint parsing error")
        return

    lhs_ineq = []
    rhs_ineq = []
    lhs_eq = []
    rhs_eq = []

    for i, sign in enumerate(inequality_signs):
        if sign == '=':
            lhs_eq.append(lhs_constraints[i])
            rhs_eq.append(rhs_constraints[i])
        elif sign == '<=':
            lhs_ineq.append(lhs_constraints[i])
            rhs_ineq.append(rhs_constraints[i])
        elif sign == '>=':
            lhs_ineq.append([-x for x in lhs_constraints[i]])
            rhs_ineq.append(-rhs_constraints[i])

    lhs_ineq = np.array(lhs_ineq) if lhs_ineq else None
    rhs_ineq = np.array(rhs_ineq) if rhs_ineq else None
    lhs_eq = np.array(lhs_eq) if lhs_eq else None
    rhs_eq = np.array(rhs_eq) if lhs_eq else None

    res = linprog(
        c=objective,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        method='highs',
    )

    if res.success:
        result_str = "Optimal solution:\n"
        for i, value in enumerate(res.x):
            result_str += f"x{i + 1} = {value:.4f}\n"

        optimal_value = -res.fun if optimization_goal == "Maximize" else res.fun
        result_str += f"Optimal value of the objective function: {optimal_value:.4f}"

        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, result_str)
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Couldn't find an optimal solution. Problem might be infeasible or unbounded.")

def toggle_appearance():
    current_mode = style.theme_use()
    new_mode = "vapor" if current_mode == "journal" else "journal"
    style.theme_use(new_mode)
    toggle_button.config(text=f"Switch to {new_mode.capitalize()} Mode")

def update_optimization_menu(event=None):
    current_state = root.state()
    optimization_menu['menu'].delete(0, 'end')
    if current_state == 'normal':
        optimization_menu['menu'].add_command(label='Minimize', command=lambda: optimization_var.set('Minimize'))
        optimization_menu['menu'].add_command(label='Maximize', command=lambda: optimization_var.set('Maximize'))
    elif current_state == 'zoomed':
        optimization_menu['menu'].add_command(label='Maximize', command=lambda: optimization_var.set('Maximize'))
        optimization_menu['menu'].add_command(label='Minimize', command=lambda: optimization_var.set('Minimize'))

root = tk.Tk()
style = Style(theme='journal')
root.title("(⁠◕⁠ᴗ⁠◕⁠✿⁠)")
root.geometry("500x800")
root.iconbitmap("icon.ico")

title_label = ttk.Label(root, text="SIMPLEX METHOD CALCULATOR", font=("Lato", 16, "bold"), style="PrimaryLabel.TLabel")
title_label.pack(pady=10)

tab_view = ttk.Notebook(root, style='journal.Tab')
tab_view.pack(pady=10, padx=10, fill='both', expand=True)

input_tab = ttk.Frame(tab_view)
constraints_tab = ttk.Frame(tab_view)
solve_tab = ttk.Frame(tab_view)

tab_view.add(input_tab, text="Inputs")
tab_view.add(constraints_tab, text="Constraints")
tab_view.add(solve_tab, text="Solve")

input_frame = ttk.Frame(input_tab)
input_frame.pack(pady=10, padx=10, fill='both', expand=True)
input_frame.configure(style='journal.TFrame')

toggle_button = ttk.Button(input_frame, text="Switch Appearance", command=toggle_appearance, style="PrimaryButton.TButton")
toggle_button.pack(anchor='w', fill='x', padx=10, pady=10)

ttk.Label(input_frame, text="Number of variables:", font=("Lato", 10), style="PrimaryLabel.TLabel").pack(anchor='w', pady=5)
num_vars_entry = ttk.Entry(input_frame, style="PrimaryEntry.TEntry", width=6)
num_vars_entry.pack(anchor='w', fill='x', padx=10)

ttk.Label(input_frame, text="Number of constraints:", font=("Lato", 10), style="PrimaryLabel.TLabel").pack(anchor='w', pady=5)
num_constraints_entry = ttk.Entry(input_frame, style="PrimaryEntry.TEntry", width=6)
num_constraints_entry.pack(anchor='w', fill='x', padx=10)

objective_frame = ttk.Frame(input_tab)
objective_frame.pack(pady=10, fill='both', expand=True)
objective_frame.configure(style='journal.TFrame')

ttk.Label(objective_frame, text="Objective function (coefficients):", font=("Lato", 10), style="PrimaryLabel.TLabel").pack(anchor='w', pady=5)

objective_entries = []
num_vars = 0

def update_objective_fields():
    try:
        num_vars = int(num_vars_entry.get())
        for widget in objective_frame.winfo_children()[1:]:
            widget.destroy()
        objective_entries.clear()
        for i in range(num_vars):
            label = ttk.Label(objective_frame, text=f"x{i + 1}:", font=("Lato", 10), style="PrimaryLabel.TLabel")
            label.pack(side='left')
            entry = ttk.Entry(objective_frame, style="PrimaryEntry.TEntry", width=6)
            entry.pack(side='left')
            objective_entries.append(entry)
    except ValueError:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Please enter a valid number of variables.")

update_objective_button = ttk.Button(input_frame, text="Update Objective Fields", command=update_objective_fields, style="PrimaryButton.TButton")
update_objective_button.pack(anchor='w', fill='x', padx=10, pady=10)

ttk.Label(input_frame, text="Optimization goal:", font=("Lato", 10), style="PrimaryLabel.TLabel").pack(anchor='w', pady=5)

# Custom Style for OptionMenu
custom_style = ttk.Style()
custom_style.theme_use(style.theme_use())
custom_style.configure('PrimaryMenubutton.TMenubutton', background='#FF5733') # Orange color
custom_style.configure('PrimaryMenubutton.TMenubutton', foreground='#FFFFFF') # White text color

optimization_var = tk.StringVar(value="Minimize")
optimization_menu = ttk.OptionMenu(input_frame, optimization_var, "Minimize", "Maximize", style='PrimaryMenubutton.TMenubutton')
optimization_menu.pack(anchor='w', fill='x', padx=10)

constraints_frame = ttk.Frame(constraints_tab)
constraints_frame.pack(pady=10, fill='both', expand=True)
constraints_frame.configure(style='journal.TFrame')

class ConstraintRow(ttk.Frame):
    def __init__(self, parent, num_vars):
        super().__init__(parent)
        self.entries = []
        for i in range(num_vars):
            ttk.Label(self, text=f"x{i + 1}:", font=("Lato", 10), style="PrimaryLabel.TLabel").pack(side='left')
            entry = ttk.Entry(self, style="PrimaryEntry.TEntry", width=6)
            entry.pack(side='left')
            self.entries.append(entry)
        self.inequality_var = tk.StringVar(value="<=")  # Changed here
        self.inequality_menu = ttk.OptionMenu(self, self.inequality_var, "<=", "<=", ">=", "=", style='PrimaryMenubutton.TMenubutton')
        self.inequality_menu.pack(side='left')
        rhs_entry = ttk.Entry(self, style="PrimaryEntry.TEntry", width=6)
        rhs_entry.pack(side='left')
        self.entries.append(rhs_entry)
        self.pack(anchor='w', fill='x', pady=3)

constraint_rows = []

def update_constraint_fields():
    try:
        num_constraints = int(num_constraints_entry.get())
        num_vars = int(num_vars_entry.get())
        for widget in constraints_frame.winfo_children():
            widget.destroy()
        constraint_rows.clear()

        for i in range (num_constraints):
            row = ConstraintRow(constraints_frame, num_vars)
            constraint_rows.append(row)
    except ValueError:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Please enter valid numbers for variables and constraints.")

update_constraints_button = ttk.Button(input_frame, text="Update Constraints", command=update_constraint_fields, style="PrimaryButton.TButton")
update_constraints_button.pack(anchor='w', fill='x', padx=10, pady=10)

solve_button = ttk.Button(solve_tab, text="Solve", command=solve_lp, style="PrimaryButton.TButton")
solve_button.pack(pady=10)

result_text = tk.Text(solve_tab, wrap=tk.WORD, width=50, height=10, font=("Helvetica", 10))
result_text.pack(pady=10)

root.bind('<Configure>', update_optimization_menu)

root.mainloop()
