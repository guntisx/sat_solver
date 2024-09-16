import sys
from typing import List, Set, Dict, Optional

class SATSolver:
    def __init__(self, clauses: List[List[int]], num_vars: int):
        self.clauses = clauses
        self.num_vars = num_vars
        self.assignments: Dict[int, bool] = {}

    def solve(self) -> Optional[Dict[int, bool]]:
        return self.dpll(self.clauses, self.assignments.copy())

    def dpll(self, clauses: List[List[int]], assignments: Dict[int, bool]) -> Optional[Dict[int, bool]]:
        clauses = self.simplify_clauses(clauses, assignments)
        
        if not clauses:
            return assignments  # All clauses satisfied
        if any(len(clause) == 0 for clause in clauses):
            return None  # Conflict detected

        # Unit Propagation
        unit = self.find_unit_clause(clauses)
        if unit:
            var, value = unit
            assignments[var] = value
            return self.dpll(clauses, assignments)

        # Pure Literal Elimination
        pure = self.find_pure_literal(clauses)
        if pure:
            var, value = pure
            assignments[var] = value
            return self.dpll(clauses, assignments)

        # Choose the first unassigned variable
        var = self.choose_variable(clauses, assignments)
        for value in [True, False]:
            new_assignments = assignments.copy()
            new_assignments[var] = value
            result = self.dpll(clauses, new_assignments)
            if result is not None:
                return result

        return None  # No solution found

    def simplify_clauses(self, clauses: List[List[int]], assignments: Dict[int, bool]) -> List[List[int]]:
        simplified = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for literal in clause:
                var = abs(literal)
                val = assignments.get(var)
                if val is not None:
                    if (literal > 0 and val) or (literal < 0 and not val):
                        satisfied = True
                        break  # Clause is satisfied
                    else:
                        continue  # Literal is False, skip
                else:
                    new_clause.append(literal)
            if not satisfied:
                simplified.append(new_clause)
        return simplified

    def find_unit_clause(self, clauses: List[List[int]]) -> Optional[tuple]:
        for clause in clauses:
            if len(clause) == 1:
                literal = clause[0]
                var = abs(literal)
                value = literal > 0
                return (var, value)
        return None

    def find_pure_literal(self, clauses: List[List[int]]) -> Optional[tuple]:
        counts: Dict[int, Set[bool]] = {}
        for clause in clauses:
            for literal in clause:
                var = abs(literal)
                val = literal > 0
                if var not in counts:
                    counts[var] = set()
                counts[var].add(val)
        for var, vals in counts.items():
            if len(vals) == 1:
                return (var, next(iter(vals)))
        return None

    def choose_variable(self, clauses: List[List[int]], assignments: Dict[int, bool]) -> int:
        # Heuristic: choose the variable that appears most frequently
        frequency: Dict[int, int] = {}
        for clause in clauses:
            for literal in clause:
                var = abs(literal)
                if var not in assignments:
                    frequency[var] = frequency.get(var, 0) + 1
        if frequency:
            return max(frequency, key=frequency.get)
        else:
            return 1  # Default to variable 1 if no variables left

def parse_dimacs(dimacs: str) -> (List[List[int]], int):
    clauses = []
    num_vars = 0
    for line in dimacs.splitlines():
        line = line.strip()
        if not line or line.startswith('c'):
            continue
        if line.startswith('p'):
            parts = line.split()
            if len(parts) != 4 or parts[1] != 'cnf':
                raise ValueError("Invalid problem line in DIMACS format.")
            num_vars = int(parts[2])
            # num_clauses = int(parts[3])  # Not used
        else:
            literals = list(map(int, line.split()))
            if literals[-1] != 0:
                raise ValueError("Clause line does not end with 0.")
            clauses.append(literals[:-1])
    return clauses, num_vars

def read_dimacs_file(filename: str) -> (List[List[int]], int):
    with open(filename, 'r') as file:
        dimacs = file.read()
    return parse_dimacs(dimacs)

def main():
    if len(sys.argv) != 2:
        print("Usage: python satsolver.py <input_dimacs_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        clauses, num_vars = read_dimacs_file(input_file)
    except Exception as e:
        print(f"Error reading DIMACS file: {e}")
        sys.exit(1)

    solver = SATSolver(clauses, num_vars)
    solution = solver.solve()

    if solution is None:
        print("UNSAT")
    else:
        print("SAT")
        # DIMACS expects a line with variable assignments ending with 0
        assignment_line = []
        for var in range(1, num_vars + 1):
            val = solution.get(var, False)
            literal = var if val else -var
            assignment_line.append(str(literal))
        assignment_line.append('0')
        print(' '.join(assignment_line))

if __name__ == "__main__":
    main()
