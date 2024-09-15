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
