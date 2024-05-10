import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.optimize import linprog

# Function to solve the linear programming problem
def solve_lp():
    try:
        # Validate number of variables and constraints
        num_vars = int(num_vars_entry.get())
        num_constraints = int(num_constraints_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for variables and constraints.")
        return

    # Validate and prepare the objective function
    optimization_goal = optimization_var.get()
    try:
        # Collect the coefficients for the objective function
        objective = []
        for i in range(num_vars):
            coeff_str = objective_entries[i].get()
            coeff = float(coeff_str)  # Ensure it is a valid float
            objective.append(coeff)

        if optimization_goal == "Maximize":
            objective = [-x for x in objective]
    except ValueError:
        messagebox.showerror("Invalid input", "Objective function error")
        return

    # Prepare constraints for processing
    lhs_constraints = []
    rhs_constraints = []
    inequality_signs = []

    try:
        # Get all constraints from the user interface
        for row in constraint_rows:
            lhs = [float(e.get()) for e in row.entries[:-1]]  # all except the last
            sign = row.inequality_menu.get()
            rhs = float(row.entries[-1].get())  # last entry is RHS
            lhs_constraints.append(lhs)
            rhs_constraints.append(rhs)
            inequality_signs.append(sign)
    except ValueError:
        messagebox.showerror("Invalid input", "Constraint parsing error")
        return

    # Separate equality and inequality constraints
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
            lhs_ineq.append([-x for x in lhs_constraints[i]])  # flip for greater-than
            rhs_ineq.append(-rhs_constraints[i])

    # Convert lists to numpy arrays
    lhs_ineq = np.array(lhs_ineq) if lhs_ineq else None
    rhs_ineq = np.array(rhs_ineq) if rhs_ineq else None
    lhs_eq = np.array(lhs_eq) if lhs_eq else None
    rhs_eq = np.array(rhs_eq) if lhs_eq else None

    # Solve the linear programming problem
    res = linprog(
        c=objective,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        method='highs',
    )

    # Handle the result
    if res.success:
        result_str = "Optimal solution:\n"
        for i, value in enumerate(res.x):
            result_str += f"x{i + 1} = {value:.4f}\n"

        optimal_value = -res.fun if optimization_goal == "Maximize" else res.fun
        result_str += f"Optimal value of the objective function: {optimal_value:.4f}"

        # Show results in a popup
        messagebox.showinfo("Solution Found", result_str)
    else:
        messagebox.showerror("LP Error", "Couldn't find an optimal solution. Problem might be infeasible or unbounded.")

# Function to toggle the appearance mode between light and dark
def toggle_appearance():
    current_mode = ctk.get_appearance_mode()
    new_mode = "Dark" if current_mode == "Light" else "Light"
    ctk.set_appearance_mode(new_mode)
    # Update the button text to reflect the new mode
    toggle_button.config(text=f"Switch to {current_mode} Mode")

# Create a customtkinter application
ctk.set_appearance_mode("System")  # Use system appearance (light or dark mode)
ctk.set_default_color_theme("blue")  # Default color theme

app = ctk.CTk()  # Create a CTkinter main window
app.title("Simplex Method Calculator")
app.geometry("800x600")

# Use tabs for different sections of the interface
tab_view = ctk.CTkTabview(app)
tab_view.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

# Create tabs for inputs, constraints, and solving
input_tab = tab_view.add("Inputs")
constraints_tab = tab_view.add("Constraints")
solve_tab = tab_view.add("Solve")

# Create a frame for inputs in the input tab
input_frame = ctk.CTkFrame(input_tab)
input_frame.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

# Add a button to toggle appearance mode
toggle_button = ctk.CTkButton(input_frame, text="Switch to Dark Mode", command=toggle_appearance)
toggle_button.pack(anchor='w', fill=ctk.X, padx=10, pady=10)

# Number of variables and constraints
ctk.CTkLabel(input_frame, text="Number of variables:").pack(anchor='w', pady=5)
num_vars_entry = ctk.CTkEntry(input_frame)
num_vars_entry.pack(anchor='w', fill=ctk.X, padx=10)

ctk.CTkLabel(input_frame, text="Number of constraints:").pack(anchor='w', pady=5)
num_constraints_entry = ctk.CTkEntry(input_frame)
num_constraints_entry.pack(anchor='w', fill=ctk.X, padx=10)

# Objective function section with labels
objective_frame = ctk.CTkFrame(input_tab)
objective_frame.pack(pady=10, fill=ctk.BOTH, expand=True)

ctk.CTkLabel(objective_frame, text="Objective function (coefficients):").pack(anchor='w', pady=5)

# Entries for objective function
objective_entries = []
num_vars = 0

def update_objective_fields():
    try:
        num_vars = int(num_vars_entry.get())
        for widget in objective_frame.winfo_children()[1:]:
            widget.destroy()  # Retain the first label, remove others
        objective_entries.clear()
        for i in range(num_vars):
            label = ctk.CTkLabel(objective_frame, text=f"x{i + 1}:")
            label.pack(side='left')
            entry = ctk.CTkEntry(objective_frame)
            entry.pack(side='left')
            objective_entries.append(entry)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number of variables.")

# Button to update objective fields
update_objective_button = ctk.CTkButton(input_frame, text="Update Objective Fields", command=update_objective_fields)
update_objective_button.pack(anchor='w', fill=ctk.X, padx=10, pady=10)

# Optimization goal
ctk.CTkLabel(input_frame, text="Optimization goal:").pack(anchor='w', pady=5)
optimization_var = ctk.StringVar(value="Minimize")
optimization_menu = ctk.CTkOptionMenu(input_frame, variable=optimization_var, values=["Minimize", "Maximize"])
optimization_menu.pack(anchor='w', fill=ctk.X, padx=10)

# Constraints section with labels, entries, and dropdown for logical operators
constraints_frame = ctk.CTkFrame(constraints_tab)
constraints_frame.pack(pady=10, fill=ctk.BOTH, expand=True)

class ConstraintRow(ctk.CTkFrame):
    def __init__(self, parent, num_vars):
        super().__init__(parent)
        self.entries = []
        for i in range(num_vars):
            ctk.CTkLabel(self, text=f"x{i + 1}:").pack(side='left')
            entry = ctk.CTkEntry(self)
            entry.pack(side='left')
            self.entries.append(entry)
        self.inequality_menu = ctk.CTkOptionMenu(self, values=["<=", ">=", "="])
        self.inequality_menu.pack(side='left')
        rhs_entry = ctk.CTkEntry(self)
        rhs_entry.pack(side='left')
        self.entries.append(rhs_entry)
        self.pack(anchor='w', fill=ctk.X, pady=3)

constraint_rows = []

# Function to update constraint fields
def update_constraint_fields():
    try:
        num_constraints = int(num_constraints_entry.get())
        num_vars = int(num_vars_entry.get())
        for widget in constraints_frame.winfo_children():
            widget.destroy()  # Remove all old entries
        constraint_rows.clear()

        for i in range (num_constraints):
            row = ConstraintRow(constraints_frame, num_vars)
            constraint_rows.append(row)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for variables and constraints.")

# Button to update constraint fields
update_constraints_button = ctk.CTkButton(input_frame, text="Update Constraints", command=update_constraint_fields)
update_constraints_button.pack(anchor='w', fill=ctk.X, padx=10, pady=10)

# Button to solve the linear programming problem
solve_button = ctk.CTkButton(solve_tab, text="Solve", command=solve_lp)
solve_button.pack(pady=10)

# Run the customtkinter event loop
app.mainloop()
