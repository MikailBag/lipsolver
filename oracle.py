import json
import typing
import argparse
import sys
import socket
import math

class InvalidPoint(Exception):
    pass

class Problem:
    _a: float
    _b: float
    _func: typing.Callable[[float], float]

    def __init__(self, a: float, b: float, objective: str, **_) -> None:
        self._a = a
        self._b = b
        self._func = lambda x: eval(objective, {'x': x, 'sin': math.sin})

    def evaluate(self, x: float) -> float:
        if x < self._a or x > self._b:
            raise InvalidPoint(f"point {x} is outside of allowed range [{self._a}, {self._b}]")
        return self._func(x)


class Logger:
    def __init__(self, log_path) -> None:
        self.log_file = open(log_path, 'w')

    def log(self, event):
        event = json.dumps(event)
        self.log_file.write(event + '\n')
        self.log_file.flush()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--problem', type=str, required=True)
    p.add_argument('--socket-file', type=str)
    p.add_argument('--socket-stdin', action='store_true')
    p.add_argument('--query-limit', type=int, required=True)
    p.add_argument('--log', type=str, required=True)
    args = p.parse_args()

    f = json.loads(args.problem)
    problem = Problem(**f)
    logger = Logger(args.log)

    if args.socket_stdin:
        sock_obj = socket.fromfd(0, socket.AF_UNIX, socket.SOCK_STREAM)
        sock_r = sock_obj.makefile('r')
        sock_w = sock_obj.makefile('w')
    else:
        # TODO: broken
        sock = open(args.socket, 'r+')
    remaining = args.query_limit
    step = 0
    logger.log({
        'type': 'Begin'
    })
    while True:
        line = sock_r.readline()
        if line.strip() == "STOP":
            point = float(sock_r.readline().strip())
            try:
                result = problem.evaluate(point)
            except InvalidPoint as ex:
                logger.log({
                    'type': 'Fail',
                    'reason': 'InvalidAnswer',
                    'description': str(ex)
                })
                exit(0)
            event = {
                'point': point,
                'result': result,
                'type': 'Answer'
            }
            logger.log(event)
            break
        try:
            f = float(line.strip())
        except:
            logger.log({
                'type': 'Fail',
                'reason': 'InvalidOutput',
                'message': f"Received invalid query {line} (likely caused by TL exceeded)"
            })
            exit(0)
        if remaining == step:
            logger.log({
                'type': 'Fail',
                'reason': 'QueryLimitExceeded',
                'message': f"Limit of {args.query_limit} queries was exhausted"
            })
            exit(0)
        try: 
            value = problem.evaluate(f)
        except InvalidPoint as ex:
            logger.log({
                'type': 'Fail',
                'reason': 'InvalidQuery',
                'description': str(ex)
            })
            exit(0)
        print(value, file=sock_w, flush=True)
        event = {
            'query': f,
            'result': value,
            'step': step,
            'type': 'Query'
        }
        logger.log(event)
        step += 1