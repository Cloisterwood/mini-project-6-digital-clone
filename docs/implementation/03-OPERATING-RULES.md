# Execution, checkpoints, and resources

## Stop at each stage or 75% context utilization

This is an execution rule for every future Codex session, not a guarantee that the assistant can read its own remaining context precisely.

1. At session start read the handoff and current stage only after reviewing the shared rules. Check `git status`/`git diff`; never overwrite unrelated work.
2. Monitor the assistant's context indicator when available (the VS Code Codex indicator, or the ZCode session's context usage). Begin checkpoint preparation around 65–70% used; at **75% used / 25% remaining**, stop new implementation and save a handoff. Subscription usage percentage is a different limit and must not substitute for context usage.
3. If context telemetry is unavailable, state that explicitly. Ask the user to signal the UI reading; use conservative small substeps and checkpoint at least after each substantial module or approximately 20 tool interactions. This fallback cannot guarantee an exact 75% boundary.
4. Before any long-running step — corpus download (~358 MB), knowledge-base indexing, full evaluation run — checkpoint proactively. Do not load the full 2,900-line July plan into a session; stages link to the specific July task needed.
5. On a stop, finish only the smallest safe file write/checkpoint operation, then record current state. Do not start another build stage. Save unsaved edits, but do not label unfinished code verified.
6. If a long script is running (download, indexing, evaluation), record process/session ID, log paths, and progress; never launch a duplicate download or index build on resume. Partial artifacts are either rebuilt or verified before use — never trusted silently.
7. Update `HANDOFF.md`, the iteration log if relevant, and the Linear issue. Record tests actually run, exact commands/results, artifacts, errors, next action, current model, and the context reading or "unavailable."
8. Review/stage named files, commit a clear milestone or WIP checkpoint, push to the confirmed GitHub remote, verify the remote SHA. If blocked, preserve local files/commit and explicitly list pending push/Linear sync. A Git commit saves locally; a push saves to GitHub.
9. End with `STOP: S<n> complete` or `STOP: context checkpoint inside S<n>`, plus the next prompt. The user starts a fresh chat and says "Resume the handoff; finish only the current stage" or "Continue with the next stage." Automatic context compaction does not authorize continuing past a stop.

## Model routing and escalation

Use OpenAI assistants throughout development. No Codex model change affects the graded pipeline, which uses no runtime LLM.

| Work | Preferred assistant tier |
|---|---|
| Metric/protocol correctness, threshold design, difficult debugging | Sol with appropriate reasoning; a stronger available OpenAI model if unresolved |
| Normal implementation and reviews | Sol (user reports "Codex Sol 5.1" as the VS Code assist; S0 records the actual picker labels) |
| Well-specified scripts, plotting, running verified commands | Terra if available; otherwise Sol |
| Small documentation, status updates, formatting | Luna if available; otherwise the current assistant |

"Sol," "Terra," and "Luna" are routing preferences, not guaranteed model IDs. Record the selected model. The human changes the picker if the agent cannot. Work sequentially; no parallel agents.

**Running a stage in ZCode instead:** the tier table applies only to VS Code/Codex sessions. A ZCode session uses its own model — do not pretend to switch tiers. The stop/handoff discipline, escalation-to-human rule, Linear and GitHub procedure, and all acceptance checks are identical in both runners. Record in the handoff which runner and model executed each stage.

Failure procedure:

1. Save the failing command, root error, environment, test case, and working diff. Distinguish code defect, missing access, bad data, and unmet performance target.
2. Make one evidence-based repair and rerun the smallest relevant check. Do not repeatedly rerun a failed long job unchanged.
3. If still unresolved, request a stronger **available** OpenAI model: "S<n>, step <x> failed with <error>. Tried <repair>, result <result>. Please switch to <available model> for this bounded diagnosis. Handoff saved at <path>." The failed unit may be repeated; completed work stays preserved.
4. After two unsuccessful repair attempts on the same blocker, stop for a human decision with evidence. Missing credentials or data require a human, not a higher model.
5. Record `failed`, `interrupted`, and `completed` distinctly in the handoff. Never upgrade a subscription automatically.

## Linear tracking

Use the Linear skill/MCP integration for issue operations; the user completes browser OAuth once in Stage 0. Create project `Mini-project 6 — Enron digital clone` with issues MP6-S0…S9 (titles and acceptance checks from 01-STAGES.md; record real IDs in RESOURCES.md). Map to the workspace's actual statuses: Todo → In Progress → Done, with Blocked where needed. Do not mark Done solely because code exists — acceptance checks must pass with recorded evidence.

At every stop update: completed checks, failed checks, GitHub commit, artifact paths, next action, and human blockers. Maintain a local `docs/LINEAR_SYNC.md` queue if the connector fails; label it pending and synchronize on the next successful connection. Local tracking is a temporary fallback, not completion of the Linear requirement. Do not assign or notify other people without user instruction.

## GitHub saving

Stage 0 resolves owner/name and visibility (expected: private repo under `Cloisterwood`; gh CLI is authenticated on this Mac — verify inside VS Code too). Inspect `git status`, `git diff`, and `git remote -v` whenever applicable.

Before the first add, ignore `.venv/`, `.env*` (allow a value-free example), `__pycache__/`, `.pytest_cache/`, `.DS_Store`, `data/raw/`, `data/emails/`, `*.joblib`, and large binaries. Keep source, configs, docs, small JSON artifacts (`style_profile_*.json`, `chunks_metadata.json`, `eval_results.json`, decision logs), and the 6 PNGs. If `index.faiss` exceeds ~50 MB, ignore it and document the rebuild command. Never commit datasets, credentials, or the venv.

Use explicit paths for staging, inspect the staged diff for secrets/large files, commit, then push. Verify `git rev-parse HEAD` equals `git ls-remote origin refs/heads/<branch>` after a successful push; save that SHA in the handoff/Linear. Never force-push, reset, or remove unrelated changes to clean up a checkpoint.

## Local Mac, Colab, and RunPod

Default: everything on the Mac (Apple M2, 24 GB). This project has no training loop — embedding ~1–3k chunks with MiniLM and FAISS search run comfortably on CPU; no GPU is expected at any stage. Colab/RunPod stay available only as a contingency if the user later scales the corpus up by an order of magnitude; if that happens, present one capped-budget option and let the user provision it. Never paste credentials into chat; verify hashes of any artifacts produced remotely before use.

## Plus and possible upgrade

Start on Plus. Codex subscription allowance, OpenAI API billing, and any GPU rental are separate resources; this plan requires **no paid API inference** (template-based generation was confirmed by the user on 2026-10-06). Upgrade to Pro only if actual Codex usage limits repeatedly block stages and the account's offered Pro tier fits the user's budget. A larger subscription does not remove stage stops or the 75% context rule. Check the account's current checkout/usage pages before purchasing; do not promise a fixed number of stages per allowance.
