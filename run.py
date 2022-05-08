import argparse
import json
import yaml
import typing
import subprocess

class Spec:
    solvers: typing.List[str]
    problems_file: str
    query_limit: int
    timeout_secs: int
    precision: float

    def __init__(self, obj) -> None:
        self.solvers = obj['solvers']
        self.problems_file = obj['problemsFile']
        self.query_limit = obj['queryLimit']
        self.timeout_secs = obj['timeoutSecs']
        self.precision = obj['precision']

def load_problems(spec: Spec) -> typing.List[str]:
    lines = open(spec.problems_file).readlines()
    lines = map(str.strip, lines)
    lines = filter(lambda s: not s.startswith('#'), lines)
    return list(lines)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--spec', type=str, required=True)
    p.add_argument('--logs-dir', type=str, required=True)
    args = p.parse_args()

    spec = yaml.safe_load(open(args.spec))
    spec = Spec(spec)

    problems = load_problems(spec)

    print(f"Loaded {len(problems)} problems and {len(spec.solvers)} solvers")

    for problem_idx in range(len(problems)):
        problem = problems[problem_idx]
        problem_data = json.loads(problem)
        print(f"running solvers on problem {problem_idx}/{len(problems)}")
        for s in spec.solvers:
            test_id = f"{s}-{problem_idx}"
            print(f"running solver {s}")
            invoke_args = ['python3', 'tools/invoke.py']
            invoke_args += ['--solver', 'solvers/' + s + '.py' ]
            invoke_args += ['--oracle', './oracle.py']
            invoke_args += ['--problem', problem]
            invoke_args += ['--query-limit', str(spec.query_limit)]
            invoke_args += ['--timeout', str(spec.timeout_secs)]
            invoke_args += ['--raw-log', args.logs_dir + '/' + test_id + '.txt']
            invoke_args += ['--desired-precision', str(10**(spec.precision))]
            invoke_args += [f"--solver-arg=--max-slope={problem_data['max_slope']}"]

            subprocess.check_call(invoke_args)

    