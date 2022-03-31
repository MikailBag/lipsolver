import argparse
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
    args = p.parse_args()

    solver_sock, oracle_sock = socket.socketpair()

    solver = subprocess.Popen(['python3', args.solver], stdin=solver_sock, stdout=solver_sock)
    oracle_cmd = ['python3', args.oracle]
    oracle_cmd += ['--problem', args.problem]
    oracle_cmd += ['--log', args.raw_log]
    oracle_cmd += ['--socket', '/dev/stdin']
    oracle_cmd += ['--query-limit', args.query_limit]

    oracle = subprocess.Popen(oracle_cmd, stdin=oracle_sock, stdout=None)

    oracle.wait(args.timeout)
    solver.wait(args.timeout)
    if oracle.returncode != 0:
        print("oracle failed", file=sys.stderr)
        exit(1)
    if solver.returncode != 0:
        print("solver failed", file=sys.stderr)
        exit(1)
    
    
