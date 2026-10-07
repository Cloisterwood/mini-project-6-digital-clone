# Iteration log

Entry 1 (Baseline) is created in Stage 6 from the real evaluation run; tuning
experiments follow in Stage 7. This file starts in Stage 2 with build notes for
deviations the stage acceptance requires recording. Entry format is fixed by
`docs/implementation/02-SYSTEM-CONTRACT.md`.

## Stage 2 notes — style profile build (2026-10-07)

- **Emails dropped by cleaning (expected loader behavior, recorded as a deviation
  note):** `mann-k` holds 8,926 raw sent-folder messages in the Kaggle corpus;
  7,414 remained usable after forwarded-chain stripping, the ≥5-word body floor,
  and the exact sender match `kay.mann@enron.com` (1,512 dropped, ≈16.9%). No
  employee switch was needed — the ≥200 threshold is cleared by ~37×.
- **Profile evolution spike at batches 71–80:** per-batch Euclidean deltas jump
  from a ~0.1–0.9 baseline to 12.53/10.31/7.20 before decaying back by batch 86.
  This coincides with a region of the mailbox with atypically long/different
  messages (EMA with α=0.3 needs ~8 batches to absorb it). Kept as-is: it is a
  real property of the corpus, not a bug; `style_score` uses raw-feature cosine
  against mean features, not the EMA vector, so evaluation is unaffected. If S6
  shows style anomalies, the S7 knob is training-email filtering (folders /
  recipient types), per 02-SYSTEM-CONTRACT tension #4.
- **Radar chart repair:** first render placed a radial-axis label over two
  feature labels; removed (the July Task 14 chart-1 sketch has no radial
  ylabel) and re-rendered.

No `CloneConfig` tunable was changed in Stage 2; no tuning entry exists yet.
