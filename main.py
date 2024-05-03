import tkinter as tk
from tkinter import messagebox
import numpy as np
import pulp as pl

class SimplexGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Simplex Method Solver")

        self.label_rows = tk.Label(master, text="Number of rows (constraints):")
        self.label_rows.grid(row=0, column=0)
        self.entry_rows = tk.Entry(master)
        self.entry_rows.grid(row=0, column=1)

        self.label_cols = tk.Label(master, text="Number of columns (variables):")
        self.label_cols.grid(row=1, column=0)
        self.entry_cols = tk.Entry(master)
        self.entry_cols.grid(row=1, column=1)

        self.label_type = tk.Label(master, text="Type of optimization:")
        self.label_type.grid(row=2, column=0)
        self.var_type = tk.StringVar(master)
        self.var_type.set("Maximize")
        self.option_type = tk.OptionMenu(master, self.var_type, "Maximize", "Minimize")
        self.option_type.grid(row=2, column=1)

        self.label_obj = tk.Label(master, text="Objective function coefficients:")
        self.label_obj.grid(row=3, column=0)
        self.entry_obj = tk.Entry(master)
        self.entry_obj.grid(row=3, column=1)

        self.label_constr = tk.Label(master, text="Constraint coefficients (separated by commas):")
        self.label_constr.grid(row=4, column=0)
        self.entry_constr = tk.Entry(master)
        self.entry_constr.grid(row=4, column=1)

        self.solve_button = tk.Button(master, text="Solve", command=self.solve)
        self.solve_button.grid(row=5, column=0, columnspan=2)

    def solve(self):
        try:
            rows = int(self.entry_rows.get())
            cols = int(self.entry_cols.get())
            obj_coeffs = list(map(float, self.entry_obj.get().split(',')))
            constr_coeffs = [list(map(float, row.split(','))) for row in self.entry_constr.get().split(';')]
            opt_type = pl.LpMaximize if self.var_type.get() == "Maximize" else pl.LpMinimize

            prob = pl.LpProblem("Simplex Problem", opt_type)

            # Define decision variables
            variables = [pl.LpVariable(f"x{i+1}", lowBound=0) for i in range(cols)]

            # Define objective function
            prob += pl.lpDot(obj_coeffs, variables)

            # Define constraints
            for i in range(rows):
                prob += pl.lpDot(constr_coeffs[i], variables) <= constr_coeffs[i][-1]

            # Solve the problem
            prob.solve()

            # Display results
            result = "Objective Value: " + str(pl.value(prob.objective)) + "\n"
            result += "Solution:\n"
            for v in prob.variables():
                result += v.name + " = " + str(v.varValue) + "\n"

            messagebox.showinfo("Result", result)

        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = SimplexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
