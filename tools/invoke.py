import argparse
import json
import socket
import subprocess
import sys


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--solver', type=str, required=True)
    p.add_argument('--oracle', type=str, required=True)
    p.add_argument('--problem', type=str, required=True)
    p.add_argument('--query-limit', type=int, required=True)
    p.add_argument('--raw-log', type=str, required=True)
    p.add_argument('--timeout', type=int, required=True)
    p.add_argument('--desired-precision', type=float, required=True)
    args = p.parse_args()

    solver_sock, oracle_sock = socket.socketpair()

    problem = json.loads(args.problem)

    solver_cmd = ['python3', args.solver]
    solver_cmd += ['--area-begin', str(problem['a'])]
    solver_cmd += ['--area-end', str(problem['b'])]
    solver_cmd += ['--precision', str(args.desired_precision)]

    solver = subprocess.Popen(
        solver_cmd, stdin=solver_sock, stdout=solver_sock)
    oracle_cmd = ['python3', args.oracle]
    oracle_cmd += ['--problem', args.problem]
    oracle_cmd += ['--log', args.raw_log]
    oracle_cmd += ['--socket-stdin']
    oracle_cmd += ['--query-limit', str(args.query_limit)]

    oracle = subprocess.Popen(oracle_cmd, stdin=oracle_sock, stdout=None)

    oracle.wait(args.timeout)
    solver.wait(args.timeout)
    if oracle.returncode != 0:
        print("oracle failed", file=sys.stderr)
        exit(1)
    if solver.returncode != 0:
        print("solver failed", file=sys.stderr)
        exit(1)
