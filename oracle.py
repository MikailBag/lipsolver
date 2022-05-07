import json
import typing
import argparse
import sys
import socket

class Problem:
    a: float
    b: float
    func: typing.Callable[[float], float]

    def __init__(self, a: float, b: float, objective: str, **_) -> None:
        self.a = a
        self.b = b
        self.func = lambda x: eval(objective, {'x': x})

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
        if line == "STOP":
            print("All queries were processed", file=sys.stderr)
            point = float(sock_r.readline().strip())
            result = problem.func(point)
            event = {
                'point': point,
                'result': result,
                'type': 'Answer'
            }
            logger.log(event)
            break
        f = float(line.strip())
        if remaining == step:
            print("Query limit exceeded", file=sys.stderr)
            logger.log({
                'type': 'Fail',
                'reason': 'QueryLimitExceeded'
            })
            exit(42)
        value = problem.func(f)
        print(value, file=sock_w, flush=True)
        event = {
            'query': f,
            'result': value,
            'step': step,
            'type': 'Query'
        }
        logger.log(event)
        step += 1