"""Combine disjoint development and held-out runs while retaining provenance."""
import json
from .run import ROOT,digest

def main():
    inputs=['results/development.json','results/heldout.json'];runs=[json.loads((ROOT/p).read_text()) for p in inputs]
    assert len({r['config_sha256'] for r in runs})==1
    rows=[row for run in runs for row in run['rows']]
    assert len({r['id'] for r in rows})==len(rows)
    result=dict(config_sha256=runs[0]['config_sha256'],environment=runs[0]['environment'],
                provenance=[dict(path=p,sha256=digest(ROOT/p),source_sha256=r['source_sha256'],elapsed_seconds=r['elapsed_seconds']) for p,r in zip(inputs,runs)],rows=rows)
    (ROOT/'results/candidates.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('Combined',len(rows),'candidates')
if __name__=='__main__':main()
