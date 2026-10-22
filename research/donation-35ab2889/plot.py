"""Plot the inherited and proposed exposed-development model witnesses."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
tasks = json.loads((ROOT / "research/readiness-20261021/portfolio.json").read_text())["tasks"]
card = next(t for t in tasks if t["id"] == "fresh-05-calibration-margin")
run = json.loads((HERE / "run-1/search-results.json").read_text())
rows = [card["incumbent"], run["rows"][1], run["rows"][3]]
labels = ["Inherited witness", "Paired move, inherited slack", "Paired move, contract floor"]
colors = ["#555555", "#0072b2", "#d55e00"]
theta = np.linspace(-90, 90, 16001)
u0 = np.sin(np.deg2rad(card["target"]["steer_deg"]))
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True,
                         gridspec_kw={"width_ratios": [2.1, 1]})
for row, label, color in zip(rows, labels, colors):
    x, phi = np.array(row["positions_lambda"]), np.array(row["phases_rad"])
    field = np.exp(1j * (2 * np.pi * np.outer(np.sin(np.deg2rad(theta)), x) + phi)).mean(axis=1)
    desired = abs(np.exp(1j * (2 * np.pi * x * u0 + phi)).mean()) ** 2
    power_db = 10 * np.log10(np.maximum(abs(field) ** 2 / desired, 1e-8))
    axes[0].plot(theta, power_db, label=label, color=color, linewidth=1.1)
for a, b in card["target"]["notches_deg"]:
    axes[0].axvspan(a, b, color="#c8c8c8", alpha=.45)
axes[0].axvline(card["target"]["steer_deg"], color="#777777", linestyle=":", linewidth=.8)
axes[0].set(xlabel="Angle from broadside (degrees)", ylabel="Nominal power / desired-direction power (dB)",
            xlim=(-65, 55), ylim=(-45, 1), title="fresh-05: ideal 16-element, six-bit phase array")
axes[0].grid(alpha=.2)
axes[0].legend(fontsize=8, loc="lower right")
for i, (row, color) in enumerate(zip(rows, colors)):
    lower = row["efficiency_error_box_lower"]
    axes[1].plot([i, i], [lower, row["metrics"]["coherent_efficiency"]], color=color, linewidth=3)
    axes[1].scatter([i], [lower], marker="s", color=color)
    axes[1].scatter([i], [row["metrics"]["coherent_efficiency"]], marker="o", color=color)
    axes[1].annotate(f"{lower:.5f}", (i, lower), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
axes[1].axhline(.85, color="#222222", linestyle="--", linewidth=1)
axes[1].set(xticks=[0, 1, 2], xticklabels=["Inherited", "Same slack", "Contract"], ylim=(.844, .916),
            xlim=(-.4, 2.4), ylabel="Coherent efficiency", title="Nominal value and error-box bound")
axes[1].grid(axis="y", alpha=.2)
fig.suptitle("Author-checked model comparison; shaded sectors are protected", fontsize=11)
fig.savefig(HERE / "comparison.svg")
svg = HERE / "comparison.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
fig.savefig(HERE / "comparison.png", dpi=170)
print("Saved comparison.svg and comparison.png")
