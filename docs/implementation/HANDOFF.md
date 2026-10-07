# Handoff — current state

**Planning date:** October 6, 2026 (plan created by ZCode from the user's pasted assignment).
**Status:** Plan complete, no code written. Next action: **Stage 0** in VS Code.

## Next action

Open this folder in VS Code (Codex) **or** in ZCode, paste the kickoff prompt from START_HERE.md, and run Stage 0 (access, destinations, decisions). Both runners follow the same plan; see "Running a stage in ZCode instead" in 03-OPERATING-RULES.md.

## Decisions already made (do not re-litigate)

1. No runtime LLM — template-based response generation (user, 2026-10-06).
2. Simulated calendar booking — no external calendar API (user, 2026-10-06).
3. Default employee Kay Mann (`mann-k`), configurable, `dasovich-j` documented fallback; Stage 2 verifies ≥200 sent emails and prints a top-20 report.
4. Plan docs only were created in this session; repo/env/Linear bootstrap happens in Stage 0 in VS Code.
5. The July plan (`docs/superpowers/plans/2026-07-04-enron-digital-clone.md`) is the technical reference; its execution instructions are superseded by `01-STAGES.md`.

## Unresolved setup details (Stage 0's job)

- [ ] GitHub repo created (private, under `Cloisterwood`) and plan pushed; URL + SHA recorded in RESOURCES.md.
- [ ] Linear project + issues MP6-S0…S9 created; real IDs/URLs recorded. In VS Code this is MCP + browser OAuth; in ZCode either the user creates the ten issues manually in the Linear UI from 01-STAGES.md, or updates queue in `docs/LINEAR_SYNC.md` until a connected session syncs them.
- [ ] Actual VS Code Codex model labels recorded (user said "Codex Sol 5.1"; MP5 notes said "Sol 6.1" — confirm what the picker shows for Sol/Terra/Luna).
- [ ] Python interpreter for `.venv` chosen in S1 after dependency resolution (system has Homebrew 3.14 and 3.13.5).

## Environment facts (verified 2026-10-06 on this Mac)

- gh CLI authenticated as `Cloisterwood` (repo scope).
- Apple M2, 24 GB RAM; no GPU needed for this project.
- `git 2.53.0`; `uv` not on PATH (plain `python3 -m venv` is fine; install uv only if preferred).
- No Linear CLI on PATH; Linear access goes through the VS Code MCP integration.

## Human-only tasks (blockers if not done)

1. **Stage 0:** confirm repo name; complete Linear OAuth when prompted.
2. **Stage 2:** none expected — employee decision pre-made; only if `mann-k` yields <200 usable emails does the fallback switch need your awareness (it is logged, not blocked).
3. **Stage 9:** run the interactive CLI yourself and accept delivery.
