#!/usr/bin/env python
"""Spec charts (July Task 14): the 6 required PNGs in docs/visualizations/.

Reads the evaluation run's data/evaluations/eval_results.json (field names
are the July Task 13 contract) and the saved style profile. Quality bar
(01-STAGES S7): descriptive titles, labeled axes, grid lines, colorblind-safe
palette, fonts >= 10 pt, 150 dpi.

Run from the repo root AFTER scripts/run_evaluation.py:
  .venv/bin/python scripts/make_visualizations.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from digital_clone.config import CloneConfig
from digital_clone.models import StyleProfile

sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.1)
plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
})
TEAL, BLUE, PINK = "#66c2a5", "#8da0cb", "#e78ac3"   # Set2 (colorblind-safe)
ORANGE = "#d95f02"                                    # dark2, target/threshold lines

OUT = ROOT / "docs" / "visualizations"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)
    print(f"wrote {OUT / name}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = CloneConfig()
    data = json.loads((cfg.eval_dir / "eval_results.json").read_text())
    records = [r for r in data["records"] if "error" not in r]
    scored = [r for r in records if r["final_score"] is not None]
    profile = StyleProfile.model_validate_json(cfg.style_profile_path.read_text())
    n = len(scored)

    # 1. Style feature radar (regenerated from the final profile; layout as
    #    accepted for the S2 chart — no radial axis label)
    names = list(profile.style_features.keys())
    vals = np.array(list(profile.style_features.values()))
    rng = vals.max() - vals.min()
    norm = (vals - vals.min()) / (rng if rng else 1.0)
    angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})
    ax.plot(angles + angles[:1], norm.tolist() + [norm[0]], color=TEAL)
    ax.fill(angles + angles[:1], norm.tolist() + [norm[0]], alpha=0.3, color=TEAL)
    ax.set_xticks(angles)
    ax.set_xticklabels(names, fontsize=11)
    ax.set_title(f"Normalized style feature profile learned from "
                 f"{profile.n_emails} of {profile.employee_name}'s sent emails\n"
                 "(min–max scaled across the 13 features; 1 = highest in-profile value)")
    save(fig, "style_feature_radar.png")

    # 2. Style score distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist([r["style_score"] for r in scored], bins=10, range=(0.90, 1.001),
            color=TEAL, edgecolor="black")
    ax.axvline(0.90, color=ORANGE, linestyle="--", linewidth=1.6,
               label="0.90 target (mean 0.999)")
    ax.set_xlabel("Style similarity score")
    ax.set_ylabel("Number of test queries")
    ax.set_title(f"Style similarity across the {n}-query evaluation set — "
                 "all queries above the 0.90 target")
    ax.legend(loc="upper left")
    save(fig, "style_score_distribution.png")

    # 3. Groundedness score distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist([r["groundedness_score"] for r in scored], bins=10,
            color=BLUE, edgecolor="black")
    ax.axvline(0.60, color=ORANGE, linestyle="--", linewidth=1.6,
               label=f"0.60 target (mean "
                     f"{np.mean([r['groundedness_score'] for r in scored]):.2f})")
    ax.set_xlabel("Groundedness score")
    ax.set_ylabel("Number of test queries")
    ax.set_title("How well responses are grounded in retrieved textbook chunks\n"
                 "(low tail = ambiguous / out-of-domain queries)")
    ax.legend(loc="upper left")
    save(fig, "groundedness_distribution.png")

    # 4. Final score breakdown per query (weighted components + threshold)
    fig, ax = plt.subplots(figsize=(13.5, 6))
    idx = np.arange(n)
    style_part = np.array([r["style_score"] for r in scored]) * cfg.style_weight
    ground_part = (np.array([r["groundedness_score"] for r in scored])
                   * cfg.groundedness_weight)
    conf_part = np.array([r["confidence_score"] for r in scored]) * cfg.confidence_weight
    ax.bar(idx, style_part, color=TEAL, label=f"style × {cfg.style_weight}")
    ax.bar(idx, ground_part, bottom=style_part, color=BLUE,
           label=f"groundedness × {cfg.groundedness_weight}")
    ax.bar(idx, conf_part, bottom=style_part + ground_part, color=PINK,
           label=f"confidence × {cfg.confidence_weight}")
    ax.axhline(cfg.fallback_threshold, color=ORANGE, linestyle="--", linewidth=1.6,
               label=f"fallback threshold {cfg.fallback_threshold}")
    ax.set_xticks(idx)
    ax.set_xticklabels([r["query"][:24] for r in scored], rotation=45,
                       ha="right", fontsize=10)
    ax.set_ylabel("Weighted contribution to final score")
    ax.set_title("Final score composition per test query vs. fallback threshold "
                 "(kept configuration)")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5))
    save(fig, "final_score_breakdown.png")

    # 5. Fallback rate by query type (with 30–40% overall target band);
    #    bar order matches the report's per-type table
    present = {r["query_type"] for r in records}
    order = [t for t in ("in_domain_factual", "in_domain_howto",
                         "out_of_domain", "ambiguous", "booking_request")
             if t in present]
    types = order + sorted(present - set(order))
    labels, rates, counts = [], [], []
    display = {"in_domain_factual": "Factual (in-domain)",
               "in_domain_howto": "How-to (in-domain)",
               "out_of_domain": "Out-of-domain", "ambiguous": "Ambiguous",
               "booking_request": "Booking request"}
    for t in types:
        rows = [r for r in records if r["query_type"] == t]
        k = sum(r["decision"] == "fallback" for r in rows)
        labels.append(f"{display.get(t, t)}\n({k}/{len(rows)} fallback)")
        rates.append(k / len(rows))
        counts.append(k)
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    bars = ax.bar(labels, rates,
                  color=sns.color_palette("Set2", len(types)), edgecolor="black")
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.02, f"{rate:.0%}",
                ha="center", fontsize=11)
    ax.axhspan(0.30, 0.40, alpha=0.15, color="green",
               label="30–40% overall target band")
    ax.set_ylabel("Fallback rate")
    ax.set_ylim(0, 1.08)
    ax.set_title("Fallback rate by query type (overall: "
                 f"{sum(counts)}/{n} = {sum(counts) / n:.0%})")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))   # fully outside axes
    ax.tick_params(axis="x", labelsize=10)
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    save(fig, "fallback_rate_by_type.png")

    # 6. Latency distribution (1 s target line; model load excluded)
    lat_ms = np.array([r["latency_seconds"] for r in records]) * 1000
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(lat_ms, bins=12, color=PINK, edgecolor="black")
    ax.axvline(1000, color=ORANGE, linestyle="--", linewidth=1.6,
               label="1 s target")
    ax.axvline(lat_ms.mean(), color="#4d4d4d", linestyle=":", linewidth=1.6,
               label=f"mean {lat_ms.mean():.0f} ms")
    ax.set_xlabel("End-to-end latency per query (ms)")
    ax.set_ylabel("Number of queries")
    ax.set_title("End-to-end query latency across the 20-query evaluation set\n"
                 "(planner construction / model load excluded, per contract)")
    ax.legend(loc="upper right")
    save(fig, "latency_distribution.png")


if __name__ == "__main__":
    main()
