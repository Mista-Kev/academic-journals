"""Run the inspected Q1/Q2 or Q3 notebook from the correct directory."""
import sys

if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12 or newer is required. Run with a supported interpreter.")

import argparse
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=['q1-q2', 'q3'])
    args = parser.parse_args()
    name = {'q1-q2': 'q1_q2_baselines.ipynb', 'q3': 'q3_baselines.ipynb'}[args.part]
    folder = ROOT / 'B_opportunities_and_analysis'
    notebook = json.loads((folder / name).read_text(encoding="utf-8"))
    # These two reviewed notebooks contain ordinary Python, not Colab magics.
    namespace = {'__name__': '__main__'}
    previous = Path.cwd()
    started = time.monotonic()
    try:
        os.chdir(folder)
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                print(f'\n--- {name}, cell {i} ---', flush=True)
                exec(compile(''.join(cell['source']), f'{name}:cell_{i}', 'exec'), namespace)
    finally:
        os.chdir(previous)
    print(f'\nCompleted {args.part} in {time.monotonic() - started:.1f}s. '
          'Printed results are from this run; the notebook file was not overwritten.')


if __name__ == '__main__':
    main()
