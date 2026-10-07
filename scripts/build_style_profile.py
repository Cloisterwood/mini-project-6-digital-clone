# scripts/build_style_profile.py
"""Download Enron corpus (Kaggle via kagglehub), learn the employee's style.

Stage 2 additions over July Task 12 Step 1:
- prints a top-20 sent-volume report across mailboxes before learning,
- falls back to the documented dasovich-j employee if mann-k yields < 200
  usable emails (recorded in docs/iteration_log.md),
- reports per-batch profile deltas (style evolution) from learner.history.

Run: python scripts/build_style_profile.py [--limit 500]"""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import kagglehub
import numpy as np
import pandas as pd

from digital_clone.agents.style_agent import ChatStyleAgent
from digital_clone.config import CloneConfig
from digital_clone.style.email_loader import is_sent_folder, load_enron_csv

MIN_EMAILS = 200
FALLBACK_EMPLOYEE = {
    "employee_folder": "dasovich-j",
    "employee_email": "jeff.dasovich@enron.com",
    "employee_name": "jeff_dasovich",
}


def count_sent_by_mailbox(csv_path: Path) -> Counter:
    """Raw sent-folder message count per mailbox (file column only, no parsing)."""
    counts: Counter = Counter()
    for df in pd.read_csv(csv_path, chunksize=20_000, usecols=["file"]):
        labels = df["file"].dropna()
        for label in labels[labels.apply(is_sent_folder)]:
            counts[label.split("/")[0]] += 1
    return counts


def print_top_mailboxes(counts: Counter, top_n: int = 20) -> None:
    print(f"\nTop {top_n} mailboxes by sent-folder volume (raw message counts):")
    for rank, (mailbox, count) in enumerate(counts.most_common(top_n), start=1):
        print(f"  {rank:>2}. {mailbox:<20} {count:>6}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    cfg = CloneConfig()
    print("Downloading Enron corpus (~358 MB, cached after first run)...")
    dataset_dir = kagglehub.dataset_download("wcukierski/enron-email-dataset")
    csv_path = Path(dataset_dir) / "emails.csv"
    print(f"Corpus cached at {csv_path}")

    print("Counting sent-folder volume per mailbox (fast pass, no parsing)...")
    counts = count_sent_by_mailbox(csv_path)
    print_top_mailboxes(counts)
    print(f"\n'{cfg.employee_folder}' raw sent-folder count: "
          f"{counts.get(cfg.employee_folder, 0)}")

    print(f"\nLoading sent emails for {cfg.employee_email} "
          f"(parsing + cleaning, sender match)...")
    emails = load_enron_csv(csv_path, cfg.employee_folder, cfg.employee_email,
                            limit=args.limit)
    print(f"Loaded {len(emails)} usable sent emails for {cfg.employee_folder}.")

    if len(emails) < MIN_EMAILS:
        n_default = len(emails)
        fallback_cfg = cfg.model_copy(update=FALLBACK_EMPLOYEE)
        print(f"NOTE: '{cfg.employee_folder}' yielded {len(emails)} < {MIN_EMAILS} "
              f"usable emails; switching to documented fallback "
              f"'{fallback_cfg.employee_folder}' ({fallback_cfg.employee_email}).")
        emails = load_enron_csv(csv_path, fallback_cfg.employee_folder,
                                fallback_cfg.employee_email, limit=args.limit)
        print(f"Loaded {len(emails)} usable sent emails for "
              f"{fallback_cfg.employee_folder}.")
        cfg = fallback_cfg
        log = Path(__file__).parent.parent / "docs" / "iteration_log.md"
        with log.open("a") as f:
            f.write(f"\n### Stage 2 note — employee fallback\n"
                    f"'mann-k' yielded {n_default} usable sent emails (< {MIN_EMAILS}); "
                    f"switched to 'dasovich-j' per the documented fallback "
                    f"(decisions log, 2026-10-06). Profile artifacts are now named "
                    f"style_profile_{cfg.employee_name}.*\n")

    assert len(emails) >= MIN_EMAILS, (
        f"Spec requires >= {MIN_EMAILS} sent emails; neither default nor fallback "
        f"yielded enough. Report counts above and pick another employee.")

    agent = ChatStyleAgent(cfg)
    profile = agent.learn(emails)
    agent.save()
    print(f"Style profile saved to {cfg.style_profile_path}")

    history = agent.learner.history
    print(f"\nBatches processed (incremental updates): {len(history)}")
    print("Per-batch profile deltas (Euclidean distance between consecutive "
          "profile vectors; style evolution):")
    for i in range(1, len(history)):
        delta = float(np.linalg.norm(history[i] - history[i - 1]))
        print(f"  batch {i + 1:>3}: delta = {delta:.4f}")

    print(f"\nMean features: {profile.style_features}")
    print(f"Greetings: {profile.greeting_patterns}")
    print(f"Sign-offs: {profile.signoff_patterns}")
    print(f"Common phrases: {profile.common_phrases}")


if __name__ == "__main__":
    main()
