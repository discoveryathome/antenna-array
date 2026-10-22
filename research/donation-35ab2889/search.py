"""Bounded discrete descent for the exposed fresh-05 calibration task.

Run from the repository root with pinned requirements. This adds research
artifacts only; the model, evaluator and accepted result files stay unchanged.
"""
import argparse
import hashlib
import itertools
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from src.evaluator import evaluate
from src.model import Objective
from trial.coherence import efficiency_lower, required_nominal_eta

TASK = "fresh-05-calibration-margin"
SEED = "35ab2889d636ae8978598a15aa094cc6"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def moves(n, paired):
    """Every alternative bin on one element; optionally +/-1,2 on any pair."""
    result = []
    for i in range(n):
        for step in range(1, 64):
            d = np.zeros(n, dtype=int)
            d[i] = step
            result.append(d)
    if paired:
        for i, j in itertools.combinations(range(n), 2):
            for a, b in itertools.product((-2, -1, 1, 2), repeat=2):
                d = np.zeros(n, dtype=int)
                d[i], d[j] = a, b
                result.append(d)
    return np.asarray(result)


def sampled(o, bins):
    w = np.exp(2j * np.pi * bins / 64)
    p0 = np.abs(w @ o.a0) ** 2
    score = np.max(np.abs(w @ o.A.T) ** 2 * o.weight, axis=1) / p0
    return score, p0


def self_check(o, q):
    one, pair = moves(len(q), False), moves(len(q), True)
    assert len(one) == len(q) * 63
    assert len(pair) == len(one) + len(q) * (len(q) - 1) // 2 * 16
    assert len(np.unique(pair % 64, axis=0)) == len(pair)
    trials = (q + pair[[0, 64, -1]]) % 64
    scores, powers = sampled(o, trials)
    for trial, score, p0 in zip(trials, scores, powers):
        p, direct_p0 = o.values(trial * 2 * np.pi / 64)
        assert np.isclose(p0, direct_p0, atol=1e-14, rtol=0)
        assert np.isclose(score, np.max(o.weight * p) / direct_p0,
                          atol=1e-13, rtol=0)


def descend(o, initial, floor, paired, max_sweeps, deadline, label):
    q = initial.copy()
    score = float(sampled(o, q[None, :])[0][0])
    deltas = moves(len(q), paired)
    history, attempts = [], []
    for sweep in range(max_sweeps):
        if time.monotonic() >= deadline:
            return q, history, attempts, "time-limit"
        proposals = (q + deltas) % 64
        scores, p0s = sampled(o, proposals)
        valid = p0s >= floor
        ranked = np.where(valid, scores, np.inf)
        best = int(np.argmin(ranked))
        record = dict(label=label, sweep=sweep, base_bins=q.tolist(),
                      scores=scores.tolist(), nominal_efficiencies=p0s.tolist())
        attempts.append(record)
        changed = bool(ranked[best] < score - 1e-12)
        history.append(dict(sweep=sweep, evaluated=len(proposals),
                            gain_feasible=int(valid.sum()), before_score=score,
                            best_move_index=best, best_score=float(scores[best]),
                            best_efficiency=float(p0s[best]), accepted=changed))
        if not changed:
            return q, history, attempts, "neighborhood-exhausted"
        q = proposals[best]
        score = float(scores[best])
    return q, history, attempts, "sweep-limit"


def run(output, max_sweeps):
    start = time.monotonic()
    deadline = start + 30 * 60
    cfg_path = ROOT / "configs/experiment.json"
    portfolio_path = ROOT / "research/readiness-20261021/portfolio.json"
    cfg = json.loads(cfg_path.read_text())
    card = next(t for t in json.loads(portfolio_path.read_text())["tasks"]
                if t["id"] == TASK)
    inherited = card["incumbent"]
    q0 = np.rint(np.asarray(inherited["phases_rad"]) * 64 / (2 * np.pi)).astype(int) % 64
    o = Objective(cfg, card["target"])
    self_check(o, q0)
    floors = [("inherited-slack", required_nominal_eta(o.u0)),
              ("contract-floor", required_nominal_eta(o.u0, slack=0) + 1e-9)]
    rows, attempts = [], []
    for floor_name, floor in floors:
        q = q0.copy()
        for paired in (False, True):
            label = floor_name + ("-pairs" if paired else "-singles")
            q, history, tried, stopped = descend(
                o, q, floor, paired, max_sweeps, deadline, label)
            attempts.extend(tried)
            phi = q * 2 * np.pi / 64
            m = evaluate(cfg, card["target"], o.x, phi)
            lower = efficiency_lower(m["coherent_efficiency"], o.u0)
            row = dict(id="fresh-05__" + label + "__35ab2889", target="fresh-05",
                       method=label, seed=SEED, positions_lambda=o.x.tolist(),
                       phases_rad=phi.tolist(), phase_bins=q.tolist(),
                       amplitudes=[1.] * len(q), metrics=m,
                       efficiency_error_box_lower=lower, design_gain_floor=floor,
                       history=history, stopped=stopped)
            row["class"] = "phase-only"
            row["established_improvement"] = bool(m["feasible"] and lower >= .85 and
                m["weighted_peak_db_upper"] < inherited["metrics"]["weighted_peak_db_lower"])
            rows.append(row)
            print(label, "upper_db", m["weighted_peak_db_upper"], "eta_lower", lower,
                  "sweeps", len(history), stopped, flush=True)
    eligible = [r for r in rows if r["metrics"]["feasible"] and
                r["efficiency_error_box_lower"] >= .85]
    winner = min(eligible, key=lambda r: r["metrics"]["weighted_peak_db_upper"])
    sources = [cfg_path, portfolio_path, Path(__file__), ROOT / "src/model.py",
               ROOT / "src/evaluator.py", ROOT / "trial/coherence.py"]
    report = dict(task=TASK, seed=SEED,
                  base="d9db8b4f07222da18b89cd4a936cbcf5e915925f",
                  source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sources},
                  environment=dict(python=platform.python_version(), numpy=np.__version__,
                                   scipy=scipy.__version__),
                  limits=dict(max_sweeps=max_sweeps, seconds=1800),
                  elapsed_seconds=time.monotonic() - start, rows=rows,
                  evaluations=sum(len(a["scores"]) for a in attempts),
                  winner=winner["id"], evidence_level="author-checked")
    output.mkdir(parents=True, exist_ok=True)
    (output / "search-results.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "attempts.jsonl").write_text("".join(json.dumps(a) + "\n" for a in attempts))
    (output / "candidate.json").write_text(json.dumps(winner, indent=2) + "\n")
    print("COMPLETE", report["evaluations"], "evaluations", report["elapsed_seconds"], "seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-sweeps", type=int, default=30)
    args = parser.parse_args()
    if args.max_sweeps <= 0:
        parser.error("--max-sweeps must be positive")
    run(args.output, args.max_sweeps)
