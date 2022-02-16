import random
import math
import json
import os
import sys

CNT_TERMS = 10
MIN_COEF = 0.01
MAX_COEF = 100


def gen_coef():
    t = random.random()
    l = math.log(MIN_COEF)
    u = math.log(MAX_COEF)
    t = l + (u-l) * t
    return math.exp(t)


def make_term():
    external_coef = gen_coef()
    internal_coef = gen_coef()
    shift = 0
    return str(external_coef) + "*sin^2(" + str(internal_coef) + "*x + " + str(shift) + ")", external_coef


def generate_formula(seed):
    random.seed(seed)
    terms = []
    L = 0
    for i in range(CNT_TERMS):
        term, lip = make_term()
        L += lip
        terms.append(term)
    return " + ".join(terms), L


if __name__ == "__main__":
    seed = os.getenv("P_SEED")
    formula, lipschitz = generate_formula(int(seed))

    problem = {
        'objective': formula,
        'a': -math.pi,
        'b': math.pi,
        'min_f': 0,
        'min_x': 1,
        'lipschitz': lipschitz
    }

    json.dump(problem, sys.stdout)
