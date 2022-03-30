import json
import typing
import argparse
import sys

class Problem:
    a: float
    b: float
    func: typing.Callable[[float], float]

    def __init__(self, a: float, b: float, func: str) -> None:
        self.a = a
        self.b = b
        self.func = lambda x: eval(func, {'x': x})




if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--problem', type=str, required=True)
    p.add_argument('--socket', type=str, required=True)
    p.add_argument('--query-limit', type=int, required=True)
    p.add_argument('--log', type=str, required=True)
    args = p.parse_args()

    f = json.load(open(args.problem))
    problem = Problem(**f)
    problem.func(problem.a)

    socket = open(args.socket, 'rw')
    log = open(p.log, 'w')
    remaining = args.query_limit
    step = 0
    while True:
        line = socket.readline()
        if line == "DONE":
            print("All queries were processed", file=sys.stderr)
            break
        f = float(line.strip())
        if remaining == step:
            print("Query limit exceeded", file=sys.stderr)
            exit(42)
        value = problem.func(f)
        print(value, file=socket)
        event = {
            'query': f,
            'result': value,
            'step': step
        }
        step += 1