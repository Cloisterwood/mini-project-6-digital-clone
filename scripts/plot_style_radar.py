# scripts/plot_style_radar.py
"""Spec chart 1: normalized style feature radar from the saved style profile.

Follows the July Task 14 chart-1 sketch: features min-max normalized to [0, 1]
across the profile's own values, colorblind-safe Set2 color, 150 dpi.
Run: python scripts/plot_style_radar.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from digital_clone.config import CloneConfig
from digital_clone.models import StyleProfile

OUT = Path(__file__).parent.parent / "docs" / "visualizations"


def main() -> None:
    cfg = CloneConfig()
    profile = StyleProfile.model_validate_json(cfg.style_profile_path.read_text())
    OUT.mkdir(parents=True, exist_ok=True)

    names = list(profile.style_features.keys())
    vals = np.array(list(profile.style_features.values()))
    rng = vals.max() - vals.min()
    norm = (vals - vals.min()) / (rng if rng else 1.0)
    angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})
    ax.plot(angles + angles[:1], norm.tolist() + [norm[0]], color="#66c2a5")
    ax.fill(angles + angles[:1], norm.tolist() + [norm[0]], alpha=0.3, color="#66c2a5")
    ax.set_xticks(angles)
    ax.set_xticklabels(names, fontsize=10)
    ax.set_title(f"Normalized style feature profile learned from "
                 f"{profile.n_emails} of {profile.employee_name}'s sent emails")
    fig.tight_layout()
    fig.savefig(OUT / "style_feature_radar.png", dpi=150)
    plt.close(fig)
    print(f"wrote {OUT / 'style_feature_radar.png'}")


if __name__ == "__main__":
    main()
