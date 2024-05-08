import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.optimize import linprog

# Function to solve the linear programming problem
def solve_lp():
    try:
        num_vars = int(num_vars_entry.get())
        num_constraints = int(num_constraints_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for variables and constraints.")
        return

    optimization_goal = optimization_var.get()

    try:
        objective = list(map(float, objective_entry.get().split()))
        if len(objective) != num_vars:
            raise ValueError("Objective function length does not match number of variables.")
        if optimization_goal == "Maximize":
            objective = [-x for x in objective]
    except ValueError as ve:
        messagebox.showerror("Invalid input", "Objective function error: " + str(ve))
        return

    lhs_constraints = []
    rhs_constraints = []
    inequality_signs = []

    try:
        for constraint_entry in constraint_entries:
            constraint = constraint_entry.get().strip()
            parts = constraint.split()
            if len(parts) != num_vars + 2:
                raise ValueError("Incorrect constraint format.")
            lhs = list(map(float, parts[:num_vars]))
            sign = parts[num_vars]
            rhs = float(parts[num_vars + 1])
            lhs_constraints.append(lhs)
            rhs_constraints.append(rhs)
            if sign == '<=':
                inequality_signs.append('le')
            elif sign == '>=':
                inequality_signs.append('ge')
            elif sign == '=':
                inequality_signs.append('eq')
            else:
                raise ValueError("Invalid inequality sign. Use '<=', '>=', or '='.")
    except ValueError as ve:
        messagebox.showerror("Invalid input", "Constraint parsing error: " + str(ve))
        return

    lhs_ineq = []
    rhs_ineq = []
    lhs_eq = []
    rhs_eq = []

    for i, sign in enumerate(inequality_signs):
        if sign == 'eq':
            lhs_eq.append(lhs_constraints[i])
            rhs_eq.append(rhs_constraints[i])
        else:
            if sign == 'le':
                lhs_ineq.append(lhs_constraints[i])
                rhs_ineq.append(rhs_constraints[i])
            else:
                lhs_ineq.append([-x for x in lhs_constraints[i]])
                rhs_ineq.append(-rhs_constraints[i])

    lhs_ineq = np.array(lhs_ineq)
    rhs_ineq = np.array(rhs_ineq)
    lhs_eq = np.array(lhs_eq) if lhs_eq else None
    rhs_eq = np.array(rhs_eq) if rhs_eq else None

    if lhs_eq is not None and lhs_eq.ndim != 2:
        messagebox.showerror("Invalid input", "Equality constraints must have two dimensions.")
        return

    res = linprog(c=objective, A_ub=lhs_ineq, b_ub=rhs_ineq, A_eq=lhs_eq, b_eq=rhs_eq, method='highs')

    if res.success:
        result_str = "Optimal solution:\n"
        for i, value in enumerate(res.x):
            result_str += f"x{i + 1} = {value:.4f}\n"

        optimal_value = -res.fun if optimization_goal == "Maximize" else res.fun
        result_str += f"Optimal value of the objective function: {optimal_value:.4f}"

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, result_str)
    else:
        messagebox.showerror("LP Error", "Couldn't find an optimal solution. Problem might be infeasible or unbounded.")

# Create the customtkinter application
ctk.set_appearance_mode("System")  # Use system appearance (light or dark mode)
ctk.set_default_color_theme("blue")  # Default color theme

app = ctk.CTk()  # Create a CTkinter main window
app.title("Linear Programming Solver")
app.geometry("400x500")

# Create a frame for inputs
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

# Number of variables and constraints
ctk.CTkLabel(input_frame, text="Number of variables:").pack(anchor='w', pady=5)
num_vars_entry = ctk.CTkEntry(input_frame)
num_vars_entry.pack(anchor='w', fill=ctk.X, padx=10)

ctk.CTkLabel(input_frame, text="Number of constraints:").pack(anchor='w', pady=5)
num_constraints_entry = ctk.CTkEntry(input_frame)
num_constraints_entry.pack(anchor='w', fill=ctk.X, padx=10)

# Objective function and optimization goal
ctk.CTkLabel(input_frame, text="Objective function (coefficients separated by spaces):").pack(anchor='w', pady=5)
objective_entry = ctk.CTkEntry(input_frame)
objective_entry.pack(anchor='w', fill=ctk.X, padx=10)

ctk.CTkLabel(input_frame, text="Optimization goal:").pack(anchor='w', pady=5)
optimization_var = ctk.StringVar(value="Minimize")
optimization_menu = ctk.CTkOptionMenu(input_frame, variable=optimization_var, values=["Minimize", "Maximize"])
optimization_menu.pack(anchor='w', fill=ctk.X, padx=10)

# Constraints section
constraints_frame = ctk.CTkFrame(input_frame)
constraints_frame.pack(pady=10, fill=ctk.BOTH, expand=True)

constraint_entries = []

def update_constraint_fields():
    try:
        num_constraints = int(num_constraints_entry.get())
        for widget in constraints_frame.winfo_children():
            widget.destroy()  # Remove all old entries
        constraint_entries.clear()

        for _ in range(num_constraints):
            entry = ctk.CTkEntry(constraints_frame)
            entry.pack(anchor='w', fill=ctk.X, padx=10, pady=3)
            constraint_entries.append(entry)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number of constraints.")

# Button to update constraint fields
update_constraints_button = ctk.CTkButton(input_frame, text="Update Constraints", command=update_constraint_fields)
update_constraints_button.pack(anchor='w', fill=ctk.X, padx=10, pady=10)

# Button to solve the linear programming problem
solve_button = ctk.CTkButton(app, text="Solve", command=solve_lp)
solve_button.pack(pady=10)

# Text widget to display results
result_text = ctk.CTkTextbox(app, height=10, width=40, wrap='word')
result_text.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

# Run the customtkinter event loop
app.mainloop()
