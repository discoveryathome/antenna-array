"""Replay the saved neighborhood experiment and audit its candidate.

The separate dense angular grid and derivative-root check are numerical checks,
not directed-rounding certificates. This script does not change accepted records.
"""
import argparse
import copy
import importlib.util
import hashlib
import json
import math
import tempfile
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from src.evaluator import validate_witness
from src.readiness import check_candidate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = "fresh-08-calibration-margin"


def independent_peaks(candidate, target):
    """Complex field implementation, uniform theta grid and stationary roots."""
    x = np.asarray(candidate["positions_lambda"])
    phi = np.asarray(candidate["phases_rad"])
    z = np.exp(1j * phi) / len(x)
    k = 2 * np.pi * x

    def power_and_derivative(u):
        terms = np.exp(1j * np.outer(np.atleast_1d(u), k)) * z
        f = terms.sum(axis=1)
        df = (terms * (1j * k)).sum(axis=1)
        return abs(f) ** 2, 2 * np.real(np.conj(f) * df)

    u0 = math.sin(math.radians(target["steer_deg"]))
    desired = float(power_and_derivative(u0)[0][0])
    regions = [("side-left", -1., u0 - .15, 1.),
               ("side-right", u0 + .15, 1., 1.)]
    regions += [(f"notch-{i}", math.sin(math.radians(a)),
                 math.sin(math.radians(b)), 16.)
                for i, (a, b) in enumerate(target["notches_deg"])]
    peaks = []
    for name, a, b, weight in regions:
        u = np.sin(np.linspace(math.asin(a), math.asin(b), 100001))
        values, derivatives = power_and_derivative(u)
        brackets = np.flatnonzero(derivatives[:-1] * derivatives[1:] < 0)
        roots = [brentq(lambda v: float(power_and_derivative(v)[1][0]),
                        u[i], u[i + 1], xtol=1e-14) for i in brackets]
        checks = np.asarray([a, b, *roots])
        p = power_and_derivative(checks)[0]
        best = int(np.argmax(p))
        peaks.append(dict(region=name, stationary_roots=len(roots),
                          sampled_max=float(values.max()),
                          numerical_peak=float(p[best]), peak_u=float(checks[best]),
                          weighted_score=float(weight * p[best] / desired)))
    score = max(p["weighted_score"] for p in peaks)
    return dict(desired_power=desired, regions=peaks, score=score,
                weighted_peak_db=10 * math.log10(score))


def extended_precision_margin(candidate, target):
    """Rearrange the angle bound to avoid acos(sqrt(eta)); not interval arithmetic."""
    ld = np.longdouble
    pi = np.arccos(ld(-1))
    u0 = np.sin(ld(str(target["steer_deg"])) * pi / 180)
    x = np.asarray(candidate["positions_lambda"], dtype=ld)
    bins = np.asarray(candidate["phase_bins"], dtype=ld)
    angle = 2 * pi * (x * u0 + bins / 64)
    eta = np.mean(np.cos(angle)) ** 2 + np.mean(np.sin(angle)) ** 2
    delta = 2 * pi / 180 + 2 * pi * abs(u0) * ld("0.005") + np.arcsin(ld("0.03"))
    bound = (np.sqrt(eta) * np.cos(delta) - np.sqrt(1 - eta) * np.sin(delta)) ** 2
    assert bound > ld("0.85")
    return dict(nominal_eta=str(eta), efficiency_lower=str(bound),
                precision_bits=int(np.finfo(ld).nmant + 1),
                note="extended precision rearrangement, not a rounding certificate")


def main(output):
    report = json.loads((HERE / "run-1/search-results.json").read_text())
    candidate = json.loads((HERE / "run-1/candidate.json").read_text())
    cfg = json.loads((ROOT / "configs/experiment.json").read_text())
    tasks = json.loads((ROOT / "research/readiness-20261021/portfolio.json").read_text())["tasks"]
    card = next(t for t in tasks if t["id"] == TASK)
    official = check_candidate(HERE / "run-1/candidate.json", TASK)
    assert not official["established_improvement"]
    assert all(row["phase_bins"] == report["rows"][0]["phase_bins"] for row in report["rows"])
    for path, expected in report["source_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    # Import the research script by path because its directory is not a module.
    spec = importlib.util.spec_from_file_location("donation_search", HERE / "search.py")
    search = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search)
    with tempfile.TemporaryDirectory(prefix="replay-", dir=HERE) as tmp:
        replay_path = Path(tmp)
        search.run(replay_path, report["limits"]["max_sweeps"])
        replay = json.loads((replay_path / "search-results.json").read_text())
        assert replay["rows"] == report["rows"]
        assert (replay_path / "attempts.jsonl").read_bytes() == (HERE / "run-1/attempts.jsonl").read_bytes()
    comparisons, alternate_cache = [], {}
    for row in [card["incumbent"], *report["rows"]]:
        metrics = validate_witness(cfg, card["target"], row)
        key = tuple(row["phases_rad"])
        if key not in alternate_cache:
            alternate_cache[key] = independent_peaks(row, card["target"])
        alternate = alternate_cache[key]
        assert abs(alternate["desired_power"] - metrics["target_power"]) < 1e-12
        assert metrics["score_lower"] - 1e-12 <= alternate["score"] <= metrics["score_upper"] + 1e-12
        comparisons.append(dict(id=row["id"], official=metrics, alternate=alternate))
    controls = []
    for label in ("wrong-target", "nonquantized", "wrong-amplitude", "false-metric", "insufficient-margin"):
        bad = copy.deepcopy(candidate)
        if label == "wrong-target":
            bad["target"] = "fresh-06"
        elif label == "nonquantized":
            bad["phases_rad"][0] += .0001
        elif label == "wrong-amplitude":
            bad["amplitudes"][0] = .99
        elif label == "false-metric":
            bad["metrics"]["score_upper"] -= .01
        else:
            nominal = next(t for t in tasks if t["id"] == "fresh-08-nominal")
            bad = copy.deepcopy(nominal["incumbent"])
        with tempfile.TemporaryDirectory(prefix="control-", dir=HERE) as tmp:
            p = Path(tmp) / "candidate.json"
            p.write_text(json.dumps(bad))
            try:
                check_candidate(p, TASK)
            except ValueError as exc:
                controls.append(dict(control=label, rejected=True, reason=str(exc)))
            else:
                raise AssertionError("failed to reject " + label)
    old = comparisons[0]["official"]
    new = official["metrics"]
    result = dict(evidence_level="author-checked", replay="exact rows and attempted-score replay passed",
                  official=official, comparisons=comparisons, failure_controls=controls,
                  outcome="No improvement; all four variants retain the inherited six-bit bins.",
                  predecessor="Adapted from PR #7 at 51c71068ae26b99585231938de139ddbdd6d99ea",
                  extended_precision=extended_precision_margin(candidate, card["target"]),
                  enclosure_resolved_improvement_db=old["weighted_peak_db_lower"] - new["weighted_peak_db_upper"],
                  numerical_limitations=["float64, without directed rounding", "stationary roots found numerically; no completeness proof",
                                         "calibration bound covers efficiency, not all perturbed performance metrics"],
                  unchanged_scope="exposed-development fresh-08; ideal isotropic array; no accepted record changes")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS exact replay, alternate checks on", len(alternate_cache), "distinct stored phase vectors, five rejecting controls")
    print("enclosure-resolved improvement dB", result["enclosure_resolved_improvement_db"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output)
