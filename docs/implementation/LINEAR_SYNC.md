# Linear sync queue (pending manual entry)

No Linear MCP in ZCode; the user creates the issues manually (decision 2026-10-07). Entries below are **pending synchronization** — paste them into the matching issues when they exist, and delete them from this file once recorded.

## MP6-S0 — Stage 0 (access, destinations, decisions)

- Status: Done (2026-10-07)
- Evidence: private repo https://github.com/Cloisterwood/mini-project-6-digital-clone, first commit `a367683319b61962cc615f2692332fab1c866ff2` (remote SHA verified equal to local HEAD); decisions logged in RESOURCES.md.

## MP6-S1 — Stage 1 (environment, package skeleton, data models)

- Status: Done (2026-10-07)
- Evidence: Python 3.14.5 `.venv`, full required stack resolved (crewai does not — requires <3.14, noted for S8); `pytest` 8/8 passed (tests written first, red verified); `.venv/bin/python -m digital_clone doctor` → OK; commit recorded in HANDOFF.md.

## MP6-S2 — Stage 2 (Enron data and ChatStyleAgent)

- Status: Done (2026-10-07)
- Evidence: `pytest` 30/30 passed (22 new tests, red-first verified); real build loaded 7,414 usable sent emails for `mann-k` (≥200 required; top-20 sent-volume report printed, `mann-k` #1 with 8,926 raw); 149 incremental batches; greeting/sign-off patterns learned; `data/models/style_profile_kay_mann.json` saved; `docs/visualizations/style_feature_radar.png` passed visual acceptance. Deviations logged in `docs/iteration_log.md`. Commit SHAs in HANDOFF.md/RESOURCES.md.
