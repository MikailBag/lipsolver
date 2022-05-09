import argparse
import json
import yaml
import typing
import subprocess


class SolverSpec:
    name: str
    extra_args: str

    def __init__(self, obj) -> None:
        self.name = obj['name']
        self.extra_args = obj.get('extraArgs', [])


class Spec:
    solvers: typing.List[SolverSpec]
    problems_file: str
    query_limit: int
    timeout_secs: int
    precision: float

    def __init__(self, obj) -> None:
        self.solvers = list(map(SolverSpec, obj['solvers']))
        self.problems_file = obj['problemsFile']
        self.query_limit = obj['queryLimit']
        self.timeout_secs = obj['timeoutSecs']
        self.precision = obj['precision']

def load_problems(spec: Spec) -> typing.List[str]:
    lines = open(spec.problems_file).readlines()
    lines = map(str.strip, lines)
    lines = filter(lambda s: not s.startswith('#'), lines)
    return list(lines)

def get_outcome(log_file: str) -> dict:
    lines = open(log_file)
    line = None
    cnt = 0
    for x in lines:
        if x.strip():
            cnt += 1
            line = x
    cnt -= 2 # do not count header and footer entries
    data = json.loads(line.strip())
    ty = data.get('type', '')
    if ty != 'Answer' and ty != 'Fail':
        return {
            'type': 'Fail',
            'reason': 'IncompleteLog',
            'description': "oracle log is incomplete",
            'lastEntry': data,
        }
    data['queryCount'] = cnt
    return data

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--spec', type=str, required=True)
    p.add_argument('--logs-dir', type=str, required=True)
    args = p.parse_args()

    spec = yaml.safe_load(open(args.spec))
    spec = Spec(spec)

    problems = load_problems(spec)

    print(f"Loaded {len(problems)} problems and {len(spec.solvers)} solvers")

    test_outcome_log = open(args.logs_dir+'/test-summary.txt', 'w')

    for problem_idx in range(len(problems)):
        problem = problems[problem_idx]
        problem_data = json.loads(problem)
        print(f"running solvers on problem {problem_idx}/{len(problems)}")
        for s in spec.solvers:
            test_id = f"{s.name}-{problem_idx}"
            print(f"running solver {s.name}")
            invoke_args = ['python3', 'tools/invoke.py']
            invoke_args += ['--solver', 'solvers/' + s.name + '.py' ]
            invoke_args += ['--oracle', './oracle.py']
            invoke_args += ['--problem', problem]
            invoke_args += ['--query-limit', str(spec.query_limit)]
            invoke_args += ['--timeout', str(spec.timeout_secs)]
            invoke_args += ['--debug-log', args.logs_dir + '/' + test_id + '-debug.txt']

            oracle_log = args.logs_dir + '/' + test_id + '-oracle.txt'
            invoke_args += ['--raw-log', oracle_log]

            invoke_args += ['--desired-precision', str(10**(spec.precision))]
            invoke_args += [f"--solver-arg=--max-slope={problem_data['max_slope']}"]
            for arg in s.extra_args:
                invoke_args.append(f"--solver-arg={arg}")

            subprocess.check_call(invoke_args)

            outcome = get_outcome(oracle_log)
            outcome['solverName'] = s.name
            outcome['problemId'] = problem_idx
            if outcome['type'] == 'Answer':
                solver_res = outcome['result']
                optimal_res = problem_data['min_f']
                solved = (solver_res <= optimal_res + (10**spec.precision))
                outcome['bestResult'] = optimal_res
                outcome['solved'] = solved
            json.dump(outcome, test_outcome_log)
            test_outcome_log.write('\n')


    