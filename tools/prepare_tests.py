from __future__ import generator_stop
import sys
import json
import yaml
import random
import subprocess


class Generator:
    def __init__(self, spec):
        self.name = spec['name']
        self.argv = spec['runCommand']['argv']
        self.env = spec['runCommand'].get('env', dict())
        self.parameters = spec['parameters']

    def invoke(self, arguments, seed, suite_id, index_in_suite):
        cwd = f"./generators/{self.name}"
        env = dict(**self.env)
        for param in self.parameters:
            if param['name'] == '$seed':
                val = str(seed)
            else:
                val = arguments[param['name']]
            env[param['var']] = val

        child = subprocess.Popen(self.argv, env=env, cwd=cwd, stdout=subprocess.PIPE)
        line = child.stdout.readline()
        val = json.loads(line)
        val['suite'] = suite_id
        val['index'] = index_in_suite
        json.dump(val, sys.stdout)
        ret = child.wait()
        assert ret == 0


def load_generators():
    generators_spec = yaml.safe_load_all(open('generators/spec.yaml'))
    gens = []
    for gen in generators_spec:
        gens.append(Generator(gen))
    return gens


def main():
    print("loading generators", file=sys.stderr)
    generators = load_generators()
    print("building test set", file=sys.stderr)
    profile = open(sys.argv[1])
    profile = yaml.safe_load(profile)
    rng = random.Random()
    rng.seed(profile['seed'])
    for req in profile['generate']:
        suite_seed = rng.randint(0, 2**30)
        suite_rng = random.Random()
        suite_rng.seed(suite_seed)
        print(
            f"Generating {req['count']} functions using generator {req['name']} with seed {suite_seed}",
            file=sys.stderr)
        for generator in generators:
            if generator.name == req['name']:
                gen = generator
                break
        else:
            raise Exception("unknown generator requested")
        for i in range(req['count']):
            gen.invoke(req.get('params', dict()), suite_rng.randint(0, 2**30), req['id'], i)
            print(flush=True)


if __name__ == '__main__':
    main()
