import numpy as np

from solver.problem import Problem

"""
Formulation
min k = sum_{j in J} y_j
s.t. 
     k >= 1
     sum_{i in I} s(i) x_{ij} <= B y_i forall j in J
     sum_{j in J} x_{ij} = 1 forall i in I
     
     y_j in {0,1} forall j in J
     x_{ij} in {0,1} forall i in I, j in J
     
     x_{ij} in {0,1} forall i in I, j in J
     y_j in {0,1} forall j in J
   
     I: items, J: bins
     s(i): size of item i
     B: bin capacity
"""
