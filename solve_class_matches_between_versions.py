# from typing import List, Tuple, Dict, Optional, Set
# import json 

# def solve_renaming1(constraints: List[Tuple[List[str], List[str]]]):
#     """
#     constraints: list of pairs ([v1 functions], [v2 functions])
#     Returns: 
#       - "unsolvable" if no mapping exists
#       - "unique", mapping if one solution
#       - "multiple", [mappings] if more than one solution
#     """

#     # Collect all function names
#     v1_funcs: Set[str] = set()
#     v2_funcs: Set[str] = set()
#     for left, right in constraints:
#         v1_funcs.update(left)
#         v2_funcs.update(right)

#     v1_funcs = list(v1_funcs)
#     v2_funcs = list(v2_funcs)

#     solutions = []

#     def is_valid(mapping: Dict[str, Optional[str]]) -> bool:
#         """Check if partial mapping violates injectivity"""
#         mapped_values = [v for v in mapping.values() if v is not None]
#         return len(mapped_values) == len(set(mapped_values))

#     def satisfies_constraints(mapping: Dict[str, Optional[str]]) -> bool:
#         """Check if all constraints are satisfied (only when all v1 assigned)"""
#         for left, right in constraints:
#             # At least one mapping from left → right
#             ok = False
#             for l in left:
#                 if l in mapping and mapping[l] in right:
#                     ok = True
#                     break
#             if not ok:
#                 return False
#         return True

#     def backtrack(i: int, mapping: Dict[str, Optional[str]]):
#         if i == len(v1_funcs):
#             if satisfies_constraints(mapping):
#                 solutions.append(mapping.copy())
#             return

#         func = v1_funcs[i]

#         # Option 1: leave unmapped
#         mapping[func] = None
#         if is_valid(mapping):
#             backtrack(i+1, mapping)

#         # Option 2: map to some v2
#         for v2 in v2_funcs:
#             mapping[func] = v2
#             if is_valid(mapping):
#                 backtrack(i+1, mapping)

#         # cleanup
#         del mapping[func]

#     backtrack(0, {})

#     if not solutions:
#         return "unsolvable", []
#     elif len(solutions) == 1:
#         return "unique", solutions[0]
#     else:
#         return "multiple", solutions

# def remove_from_constraints(constraints: List[Tuple[List[str], List[str]]], lefts, rights):
#     '''Remove lefts and rights from constraints'''
#     new_constraints = []
#     for left, right in constraints:
#         new_left = [l for l in left if l not in lefts]
#         new_right = [r for r in right if r not in rights]
#         if new_left or new_right:
#             new_constraints.append((new_left, new_right))
#     return new_constraints

# def solve_renaming(constraints: List[Tuple[List[str], List[str]]]):
#     solution = {}
#     changed_last_round = True
#     while changed_last_round:
#         lefts, rights = set(), set()
#         changed_last_round = False
#         for constraint in constraints:
#             left, right = constraint
#             if not left or not right:
#                 print(constraint)
#                 # return "unsolvable", [] 
#             if len(left) == 1 and len(right) == 1:
#                 solution[left[0]] = right[0]
#                 lefts.add(left[0])
#                 rights.add(right[0])
#                 changed_last_round = True
#         constraints = remove_from_constraints(constraints, lefts, rights)
#     return constraints, solution


# with open('constraints.json', 'r', encoding='utf-8') as f:
#     constraints = json.load(f)
# print(len(constraints))
# kind, sols = solve_renaming(constraints)
# # print(len(solve_renaming1(kind)))
# print(len(sols))
#!/usr/bin/env python3
import argparse
from typing import List, Tuple, Dict, Optional, Set
import json

def remove_from_constraints(constraints: List[Tuple[List[str], List[str]]], lefts, rights):
    """
    Remove solved functions from constraints to simplify remaining problem.
    lefts: functions from v1 that are already mapped
    rights: functions from v2 that are already mapped
    """
    new_constraints = []
    for left, right in constraints:
        new_left = [l for l in left if l not in lefts]
        new_right = [r for r in right if r not in rights]
        if new_left or new_right:
            new_constraints.append((new_left, new_right))
    return new_constraints

def solve_renaming(constraints: List[Tuple[List[str], List[str]]]):
    """
    Iterative solver that greedily resolves constraints with only one possibility.
    Returns remaining constraints and solved mappings.
    """
    solution = {}
    changed_last_round = True

    while changed_last_round:
        lefts, rights = set(), set()
        changed_last_round = False

        for constraint in constraints:
            left, right = constraint
            # If exactly one option in both sides, fix the mapping
            if len(left) == 1 and len(right) == 1:
                solution[left[0]] = right[0]
                lefts.add(left[0])
                rights.add(right[0])
                changed_last_round = True

        # Remove the solved functions from remaining constraints
        constraints = remove_from_constraints(constraints, lefts, rights)

    return constraints, solution

def main():
    parser = argparse.ArgumentParser(description="Solve function renaming constraints.")
    parser.add_argument("input_file", type=str, help="Path to input constraints JSON file")
    parser.add_argument("output_file", type=str, help="Path to output JSON file for solution")
    args = parser.parse_args()

    # Load constraints from input JSON file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        constraints = json.load(f)

    print(f"Loaded {len(constraints)} constraints.")

    # Solve the renaming problem
    remaining_constraints, solution = solve_renaming(constraints)

    print(f"Remaining constraints: {len(remaining_constraints)}")
    print(f"Number of solved mappings: {len(solution)}")

    # Save the solved mapping to the output file
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(solution, f, indent=2)

    print(f"Solution saved to {args.output_file}")

if __name__ == "__main__":
    main()
