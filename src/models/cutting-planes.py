"""
    TSP Solver
    The Dantzig, Fulkerson and Johnson (DFJ) formulation
"""
from __future__ import print_function
from ortools.linear_solver import pywraplp

import numpy as np
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 
import helper

 # Create the mip solver with the SCIP backend.
solver = pywraplp.Solver.CreateSolver('SCIP')

def all_sub_cycles(acc, x, initial, actual, nivel, length_cycle, next_node, n_nodes):
    print(next_node)
    if(nivel == length_cycle):
        acc.append(x[actual, initial])
        print("WTF: ", acc)
        solver.Add(solver.Sum(acc[1:]) <= length_cycle)
        return 
    
    for j in range(n_nodes - nivel):
        next = next_node.pop(0)
        all_sub_cycles([acc, x[actual, next]], x, initial, next, nivel + 1, length_cycle, next_node, n_nodes)
        next_node.append(actual)
    return 

def generate_constrain(x, n_nodes):
    next_node = list(range(n_nodes))
    print(next_node)
    for i in range(2, n_nodes-1):
        for j in range(0, n_nodes):
            initial = next_node.pop(0)
            all_sub_cycles([], x, initial, initial, 1, i, next_node, n_nodes)
            next_node.append(initial)

def create_data_model():
    
    # Cost[i, j] : cost to go from i to j
    costs = helper.load_data()
    n_nodes = len(costs)

    # # Inicializate boolean variable x[i, j]
    # x[i, j] is one if there a segment from i to j     
    x = {}
    for position_from in range(n_nodes):
        for position_to in range(n_nodes):
            x[position_from, position_to] = solver.IntVar(0, 1, '')

    # Subject to:

    # # Add consrains that all cities must have an arest leaving
    for i in range(n_nodes):
        solver.Add(solver.Sum(x[i, j] for j in range(n_nodes)) == 1)

    # # Add consrains that all cities must have an arest arriving
    for j in range(n_nodes):
        solver.Add(solver.Sum(x[i, j] for i in range(n_nodes)) == 1)

    # # Add constrains DFJ to sub-tour elimination
    generate_constrain(x, n_nodes)
    
    # # Goal function min
    function_goal = []
    for i in range(n_nodes):
        for j in range(n_nodes):
            function_goal.append(costs[i][j] * x[i, j])

    # Set goal function to minimizate
    solver.Minimize(solver.Sum(function_goal))
    
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    else:
        print('The problem does not have an optimal solution.')

def main():
    create_data_model()

if __name__ == '__main__':
    main()
