"""Recompute every claimed nominal metric from candidate construction data."""
import argparse
import json
from pathlib import Path
from .evaluator import validate_witness
from .run import digest
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--file',default='results/candidates.json');p.add_argument('--row');args=p.parse_args()
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());data=json.loads((ROOT/args.file).read_text())
    assert data['config_sha256']==digest(ROOT/'configs/experiment.json'),'configuration hash mismatch'
    targets={t['id']:t for t in cfg['targets']}
    selected=[r for r in data['rows'] if args.row is None or r['id']==args.row]
    assert selected,'no selected rows'
    assert len({r['id'] for r in selected})==len(selected),'duplicate IDs'
    for row in selected:validate_witness(cfg,targets[row['target']],row)
    print(f"PASS: {len(selected)} witnesses; independent trig sums, hardware constraints, all metrics and between-grid peak bounds recomputed.")

if __name__=='__main__':main()
