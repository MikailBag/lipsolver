"""
Shekel's function generator
"""
import random
import os
import gridsearch as gs
import sympy as sym
import json
import sys
import math


class ShekelGen:
    """
    Shekel test functions generator
    Source: Sergeyev, Y. D., Nasso, M. C., Mukhametzhanov, M. S., Kvasov, D. E. (2021).
        Novel local tuning techniques for speeding up one-dimensional algorithms in expensive global optimization using Lipschitz derivatives.
        Journal of Computational and Applied Mathematics, 383, 113134.
    Attributes:
        k_range: the range for k parameter
        a_range: the range for a parameter
        c_range: the range for c parameter
        N: number of terms in the sum
        gs_step: the grid step size
    """

    def __init__(self):
        self.k_range = (1,3)
        self.a_range = (0,10)
        self.c_range = (0.1, 0.3)
        self.N = 10
        self.gs_step = 1e-5

    def gen_one_problem(self, reverse = False):
        """
        Generates Schekel's or reverse Shekel's function
        Args:
            n: the number of a problem
            reverse: if True - generate reverse Shekel's function, if False - normal one

        Returns:
            dict describing problem
        """
        formula = ""
        max_slope = 0.0
        for i in range(0, self.N):
            a = random.uniform(self.a_range[0], self.a_range[1])
            k = random.uniform(self.k_range[0], self.k_range[1])
            c = random.uniform(self.c_range[0], self.c_range[1])
            term = ("1./(" if reverse else "-1/(") + str(k*k) + " * (10. * x - " + str(a) + ")**2 + " + str(c) + ")"
            # function (modulo details): 1/(k * x^2 + c)
            # derivative (2kx)/(kx^2+c)^2
            # Wolfram says global maxima fo derivative is \frac{3\sqrt{3}}{8}\sqrt{\frac{k}{c^3}}
            max_slope += 3 * math.sqrt(3) / 8.0 * 10.0 * k / (c ** 1.5)
            formula += term if i == 0 else " + " + term

        sym_objective = sym.sympify(formula)
        x = sym.symbols('x')
        objective = sym.lambdify(x, sym_objective)
        a = 0.
        b = 1.
        true_min = gs.grid_search(objective, a, b, self.gs_step)
        dct = dict(objective=formula, a=0., b=1., min_f=true_min[1], min_x=true_min[0], max_slope=max_slope)
        return dct

if __name__ == "__main__":
    seed = os.getenv("P_SEED")
    assert seed is not None

    random.seed(int(seed))

    kind = os.getenv("P_KIND")
    assert kind in ["normal", "reverse"]
    # Reverse Shekel (True) or normal Shekel (False) functions
    rshek = kind == "reverse"

    sk_gen = ShekelGen()
    problem = sk_gen.gen_one_problem(rshek)
    
    json.dump(problem, sys.stdout)