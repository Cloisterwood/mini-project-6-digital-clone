# Resources — confirmed and to-confirm

## Confirmed (2026-10-06)

- **GitHub account:** `Cloisterwood` (gh CLI authenticated on this Mac; token has `repo` scope). Repo to be created in S0 — proposed name `mini-project-6-digital-clone`, **private**. Record final name/URL/visibility here after S0.
- **Datasets (resolved by the July plan; no links needed from the user):**
  - Enron corpus: Kaggle `wcukierski/enron-email-dataset` (~358 MB ZIP; `emails.csv` with columns `file`, `message`) via `kagglehub.dataset_download` — public, no Kaggle credentials required.
  - Textbooks: HuggingFace `open-phi/textbooks` (streamed; filter `field` containing "computer"; columns `markdown`, `topic`, `field`).
- **Hardware:** Apple M2, 24 GB — sufficient for the entire pipeline on CPU; no Colab/RunPod expected.
- **Implementation reference:** `docs/superpowers/plans/2026-07-04-enron-digital-clone.md` (Tasks 1–16 with code and tests).

## Stage 0 record (2026-10-07)

- **GitHub repo:** https://github.com/Cloisterwood/mini-project-6-digital-clone (private, under `Cloisterwood`). First pushed commit `a367683319b61962cc615f2692332fab1c866ff2`; remote SHA verified equal to local HEAD.
- **Runner/model for S0:** ZCode session, model GLM-5.3-Flash. Sol/Terra/Luna tier table not applicable (VS Code-only, per 03-OPERATING-RULES).
- **Linear (user decision 2026-10-07):** the user creates the ten stage issues manually in the Linear UI; record IDs/URLs here once created. Statuses until then live in this file and HANDOFF.md.
  - Linear workspace/team: ________  |  project URL: ________  |  issue IDs MP6-S0…S9: ________
- **VS Code Codex model labels:** not needed for a ZCode run; confirm when a stage runs in VS Code.
- **Python version for `.venv`:** to be chosen in S1 after dependency resolution (system offers Homebrew 3.14 and 3.13.5).

## Notes

- The user's pasted assignment lost its HuggingFace/Kaggle hyperlink URLs in copy-paste; the dataset identities above come from the July plan's locked decisions and the assignment's own descriptions (mailbox-style Enron corpus; `open-phi/textbooks`). If Stage 2 or 3 finds a mismatch with the actual data, stop and re-confirm with the user before substituting a different source.
- Prior project `mini-project-5` used the same staged-plan pattern; its `docs/implementation/RESOURCES.md` is the format precedent.
