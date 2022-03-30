import argparse
import yaml

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--spec', type=str, required=True)
    args = p.parse_args()

    spec = yaml.safe_load(open(args.spec))
    