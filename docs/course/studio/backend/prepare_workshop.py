"""Copy the teaching workshop without generated files; refuse existing targets."""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path, help='New directory, usually lab-workshop in your learning repo')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2] / 'workshop'
    target = args.target.resolve()
    if not source.is_dir():
        parser.error(f'Cannot find workshop source: {source}')
    if target.exists():
        parser.error('Target already exists; choose a new directory. Nothing was replaced.')
    if source == target or source in target.parents:
        parser.error('Target must be outside the source workshop.')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(
        'node_modules', 'dist', '__pycache__', '.pytest_cache', '*.db', '*.db-*', '*.sqlite*'))
    print(f'Created learning copy: {target}')
    print('No database, dependency folder, or built frontend was copied.')


if __name__ == '__main__':
    main()
