"""Record the pre-existing exact-float robustness mismatch without changing it."""
import hashlib
import json
import math
from pathlib import Path
import platform
import numpy as np
from src.robustness import worst_case
from src.check import tables

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    cfg = json.loads((ROOT/'configs/experiment.json').read_text())
    data = json.loads((ROOT/'results/candidates.json').read_text())
    rows = {r['id']:r for r in data['rows']}
    stored = json.loads((ROOT/'results/robustness.json').read_text())
    differences = []
    for r in stored['rows']:
        current = worst_case(cfg,rows[r['id']])
        for key,actual in current.items():
            expected = r['worst_case'][key]
            if actual != expected:
                differences.append(dict(id=r['id'],metric=key,stored=expected,current=actual,
                    absolute_difference=abs(actual-expected),ulps=abs(actual-expected)/math.ulp(expected)))
    tables(cfg,data)
    report = dict(command='python -m src.check',status=(
        'FAIL in existing exact-dictionary equality at src/check.py:66' if differences else
        'Exact worst-case values agree on this environment; full src.check not run by this diagnostic.'),
        environment=dict(python=platform.python_version(),numpy=np.__version__),differences=differences,
        passed_before_failure=['72 stored reconstructions and uniform-angle audits','protocol checks','literature inventory'],
        separately_checked='tables(): frontier witnesses, best-of-local-portfolio values, summary and artifact hashes passed',
        not_completed='Full robustness replay; no assertion was relaxed and no stored value was rewritten.',
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('src/check.py','src/robustness.py','results/robustness.json')})
    (HERE/'baseline-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Pre-existing exact-float mismatches:',len(differences),'; all',sorted(set(d['ulps'] for d in differences)),'ULP')


if __name__=='__main__':
    main()
