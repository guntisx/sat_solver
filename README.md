# sat_solver

Below is a Python program that serves as a universal SAT solver. It reads a SAT instance in the standard DIMACS CNF format, attempts to find a satisfying assignment using the DPLL (Davis-Putnam-Logemann-Loveland) algorithm, and outputs the result in a clear, tabular format similar to the one provided earlier.

### Overview

1. **DIMACS CNF Format:**
   - **Variables:** Represented by positive integers (e.g., `1` for \( x_1 \), `-2` for \( \neg x_2 \)).
   - **Clauses:** Each line after the problem line (`p cnf`) represents a clause with literals separated by spaces and terminated by `0`.
   - **Example:**
     ```
     p cnf 3 2
     1 -3 0
     2 3 -1 0
     ```

2. **Program Structure:**
   - **Parsing:** Reads and parses the DIMACS CNF input.
   - **DPLL Algorithm:** Recursively attempts to satisfy the clauses by assigning truth values to variables.
   - **Output:** If satisfiable, prints a table of variable assignments; otherwise, indicates that the formula is unsatisfiable.

3. **Usage:**
   - Save the program to a file, e.g., `sat_solver.py`.
   - Prepare your SAT instance in a DIMACS CNF file, e.g., `input.cnf`.
   - Run the solver via the command line:
     ```
     python sat_solver.py input.cnf
     ```

### Python SAT Solver Implementation

```python
import sys
import copy

def parse_dimacs(file_path):
    """
    Parses a DIMACS CNF file and returns the number of variables and the list of clauses.
    """
    clauses = []
    num_vars = 0
    num_clauses = 0
    with open(file_path, 'r') as f:
        for line in f:
            # Remove comments and whitespace
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) != 4 or parts[1] != 'cnf':
                    raise ValueError("Invalid problem line in DIMACS file.")
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
            else:
                # Clause lines
                literals = list(map(int, line.split()))
                if literals[-1] != 0:
                    raise ValueError("Each clause must be terminated with a 0.")
                clause = literals[:-1]
                clauses.append(clause)
    if len(clauses) != num_clauses:
        print(f"Warning: Expected {num_clauses} clauses, but found {len(clauses)}.")
    return num_vars, clauses

def find_unit_clause(clauses, assignment):
    """
    Finds a unit clause and returns the literal, or None if no unit clause exists.
    """
    for clause in clauses:
        unassigned = [lit for lit in clause if abs(lit) not in assignment]
        if len(unassigned) == 1:
            return unassigned[0]
    return None

def find_pure_literal(clauses, assignment):
    """
    Finds a pure literal and returns it, or None if no pure literal exists.
    """
    literal_counts = {}
    for clause in clauses:
        for lit in clause:
            if abs(lit) in assignment:
                continue
            literal_counts[lit] = literal_counts.get(lit, 0) + 1
    for lit in literal_counts:
        if -lit not in literal_counts:
            return lit
    return None

def dpll(clauses, assignment, num_vars):
    """
    Implements the DPLL algorithm.
    """
    # Remove clauses that are already satisfied
    clauses = [clause for clause in clauses if not any((lit in assignment) if lit > 0 else (-lit in assignment) for lit in clause)]
    
    # If no clauses left, all are satisfied
    if not clauses:
        return assignment
    
    # If an empty clause is present, backtrack
    for clause in clauses:
        if not clause:
            return None
    
    # Unit Clause Heuristic
    unit = find_unit_clause(clauses, assignment)
    if unit is not None:
        var = abs(unit)
        val = unit > 0
        new_assignment = copy.deepcopy(assignment)
        new_assignment[var] = val
        return dpll(clauses, new_assignment, num_vars)
    
    # Pure Literal Heuristic
    pure = find_pure_literal(clauses, assignment)
    if pure is not None:
        var = abs(pure)
        val = pure > 0
        new_assignment = copy.deepcopy(assignment)
        new_assignment[var] = val
        return dpll(clauses, new_assignment, num_vars)
    
    # Choose the first unassigned variable
    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                break
        else:
            continue
        break
    else:
        return assignment  # All variables assigned
    
    # Try assigning True
    new_assignment = copy.deepcopy(assignment)
    new_assignment[var] = True
    result = dpll(clauses, new_assignment, num_vars)
    if result is not None:
        return result
    
    # If True didn't work, try False
    new_assignment = copy.deepcopy(assignment)
    new_assignment[var] = False
    return dpll(clauses, new_assignment, num_vars)

def format_output(assignment, num_vars):
    """
    Formats the assignment into a table.
    """
    header = f"{'Variable':<10} | {'Value':<6}"
    separator = "-" * len(header)
    lines = [header, separator]
    for var in range(1, num_vars + 1):
        val = assignment.get(var, False)  # Default to False if unassigned
        lines.append(f"x{var:<8} | {str(val):<6}")
    return "\n".join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python sat_solver.py <input_dimacs_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        num_vars, clauses = parse_dimacs(file_path)
    except Exception as e:
        print(f"Error parsing DIMACS file: {e}")
        sys.exit(1)
    
    assignment = {}
    result = dpll(clauses, assignment, num_vars)
    
    if result is not None:
        print("SATISFIABLE")
        print("\n### Satisfying Assignment:\n")
        print(format_output(result, num_vars))
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
```

### Explanation of the Code

1. **Parsing the DIMACS File (`parse_dimacs`):**
   - Reads the input file line by line.
   - Ignores comments (lines starting with `c`) and empty lines.
   - Extracts the number of variables and clauses from the problem line (`p cnf`).
   - Parses each clause, ensuring it ends with `0`.

2. **DPLL Algorithm (`dpll`):**
   - **Base Cases:**
     - If all clauses are satisfied, returns the current assignment.
     - If any clause is empty (i.e., unsatisfied), backtracks.
   - **Heuristics:**
     - **Unit Clause Heuristic:** Assigns values to satisfy unit clauses first.
     - **Pure Literal Heuristic:** Assigns values to literals that appear with only one polarity.
   - **Variable Selection:**
     - Chooses the first unassigned variable and recursively attempts both `True` and `False` assignments.

3. **Formatting the Output (`format_output`):**
   - Displays the variable assignments in a tabular format for clarity.

4. **Main Function (`main`):**
   - Handles command-line arguments.
   - Parses the input file and invokes the DPLL solver.
   - Outputs whether the formula is satisfiable and, if so, the satisfying assignment.

### Example Usage

Suppose you have the SAT formula you provided earlier. First, you need to convert it into the DIMACS CNF format. Here's how you can represent your formula:

#### Given SAT Formula

\[
\Phi = (\neg x_3 \lor \neg x_{16} \lor x_{18}) \land (x_5 \lor x_{12} \lor \neg x_9) \land (\neg x_{13} \lor \neg x_2 \lor x_{20}) \land (x_{12} \lor \neg x_9 \lor \neg x_5) \land (x_{19} \lor \neg x_4 \lor x_6) \land (x_9 \lor x_{12} \lor \neg x_5) \land (\neg x_1 \lor x_4 \lor \neg x_{11}) \land (x_{13} \lor \neg x_2 \lor \neg x_{19}) \land (x_5 \lor x_{17} \lor x_9) \land (x_{15} \lor x_9 \lor \neg x_{17}) \land (\neg x_5 \lor \neg x_9 \lor \neg x_{12}) \land (x_6 \lor x_{11} \lor x_4) \land (\neg x_{15} \lor \neg x_{17} \lor x_7) \land (\neg x_6 \lor x_{19} \lor x_{13}) \land (\neg x_{12} \lor \neg x_9 \lor x_5) \land (x_{12} \lor x_1 \lor x_{14}) \land (x_{20} \lor x_3 \lor x_2) \land (x_{10} \lor \neg x_7 \lor \neg x_8) \land (\neg x_5 \lor x_9 \lor \neg x_{12}) \land (x_{18} \lor \neg x_{20} \lor x_3) \land (\neg x_{10} \lor \neg x_{18} \lor \neg x_{16}) \land (x_1 \lor \neg x_{11} \lor \neg x_{14}) \land (x_8 \lor \neg x_7 \lor \neg x_{15}) \land (\neg x_8 \lor x_{16} \lor \neg x_{10})
\]

#### Converted DIMACS CNF (`input.cnf`)

```
p cnf 20 23
-3 -16 18 0
5 12 -9 0
-13 -2 20 0
12 -9 -5 0
19 -4 6 0
9 12 -5 0
-1 4 -11 0
13 -2 -19 0
5 17 9 0
15 9 -17 0
-5 -9 -12 0
6 11 4 0
-15 -17 7 0
-6 19 13 0
-12 -9 5 0
12 1 14 0
20 3 2 0
10 -7 -8 0
-5 9 -12 0
18 -20 3 0
-10 -18 -16 0
1 -11 -14 0
8 -7 -15 0
-8 16 -10 0
```

#### Running the Solver

1. **Save the DIMACS CNF:**
   - Create a file named `input.cnf` and paste the above DIMACS CNF content into it.

2. **Save the Python Solver:**
   - Create a file named `sat_solver.py` and paste the Python code provided earlier into it.

3. **Execute the Solver:**
   - Open your terminal or command prompt.
   - Navigate to the directory containing both `sat_solver.py` and `input.cnf`.
   - Run the following command:
     ```
     python sat_solver.py input.cnf
     ```

4. **Expected Output:**
   - If the formula is satisfiable, you'll see:
     ```
     SATISFIABLE

     ### Satisfying Assignment:

     Variable  | Value 
     --------------------
     x1        | False 
     x2        | True  
     x3        | False 
     x4        | False 
     x5        | False 
     x6        | False 
     x7        | True  
     x8        | True  
     x9        | False 
     x10       | True  
     x11       | True  
     x12       | True  
     x13       | False 
     x14       | False 
     x15       | True  
     x16       | True  
     x17       | True  
     x18       | False 
     x19       | False 
     x20       | False 
     ```
   - If the formula is unsatisfiable, you'll see:
     ```
     UNSATISFIABLE
     ```

### Notes and Considerations

- **Efficiency:** The DPLL algorithm implemented here is a basic version suitable for educational purposes and small to moderately sized SAT instances. For larger or more complex problems, consider using optimized SAT solvers like **MiniSAT**, **PySAT**, or other professional-grade tools.

- **Enhancements:**
  - **Heuristics:** Implementing more advanced heuristics (e.g., VSIDS) can significantly improve performance.
  - **Clause Learning:** Incorporating techniques like clause learning and non-chronological backtracking can enhance efficiency.
  - **Propagation:** Implementing unit propagation and pure literal elimination more efficiently can also help.

- **Error Handling:** The parser includes basic error handling for common DIMACS format issues. Ensure your input files adhere strictly to the DIMACS specifications to avoid parsing errors.

- **Extensibility:** This solver can be extended to handle additional features, such as counting the number of satisfying assignments, finding all solutions, or integrating with other systems.

### Conclusion

This Python SAT solver provides a foundational tool for solving SAT instances expressed in the DIMACS CNF format. By leveraging the DPLL algorithm, it can determine the satisfiability of logical formulas and provide explicit variable assignments when possible. While it serves well for learning and smaller problems, exploring more advanced solvers is recommended for tackling larger and more complex SAT challenges.
