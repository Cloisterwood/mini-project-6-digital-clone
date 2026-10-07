# Mini-project 6: staged implementation

Planning date: October 6, 2026. Status: plan created; no code written yet. Next action: Stage 0 in VS Code.

Build a 5-agent "digital clone" of an Enron employee (default: Kay Mann) that answers questions in their email style, grounded in a computer-science textbook knowledge base, with weighted quality evaluation and calendar-booking fallback. OpenAI models assist development only — the graded pipeline is deterministic and needs no runtime LLM or paid API inference.

## Start a session (VS Code/Codex or ZCode — both work)

Open `/Users/jeanneduke/newline-class-projects/mini-project-6` as the folder in either tool. Paste this into the chat:

> Read START_HERE.md, docs/implementation/01-STAGES.md, docs/implementation/02-SYSTEM-CONTRACT.md, docs/implementation/03-OPERATING-RULES.md, and docs/implementation/HANDOFF.md. Execute only the next incomplete stage. Inspect the workspace before changes. Stop at stage completion or 75% context utilization, whichever comes first. Save a handoff, update Linear, and commit/push reviewed project files to the confirmed GitHub repository. If an integration is unavailable, record pending synchronization honestly. Ask only for information, access, or human decisions that block this stage. Do not start the next stage until I say continue.

- **In VS Code:** terminal commands run in the integrated terminal; prompts run in Codex chat. The Sol/Terra/Luna routing table in 03-OPERATING-RULES applies here.
- **In ZCode:** paste the same prompt into a ZCode session opened on this folder. The tier routing does not apply (the session uses its own model) — everything else is identical. ZCode has no Linear MCP, so either create the ten stage issues yourself from 01-STAGES.md (~10 minutes) or let the agent queue updates in `docs/LINEAR_SYNC.md`; the kickoff prompt's "record pending synchronization honestly" line covers this.
- **For maximum visibility while learning:** keep the same folder open in VS Code next to the ZCode session — every file change and commit appears live in the Source Control view, so commits become your timeline. Optionally run the ZCode session with a permission mode that asks before each edit.

## Confirmed decisions (2026-10-06, with the user)

1. **No runtime LLM.** Response generation is template-based (retrieved chunks + learned greeting/sign-off), per the July plan. The <1s latency target and offline test suite depend on this. OpenAI models are used only as the development assistant.
2. **Simulated calendar booking.** Generated link + slots from FallbackAgent; no external calendar API.
3. **Default employee: Kay Mann** (`kay.mann@enron.com`, folder `mann-k`), configurable; documented fallback `dasovich-j` if parsing yields <200 usable sent emails. Stage 2 verifies the count and reports top senders.
4. Development assistant tiers: Sol (default), Terra, Luna per the routing table; escalate upward on failure per 03-OPERATING-RULES.

## Read in this order

1. [Stage plan](docs/implementation/01-STAGES.md): ten bounded build stages (S0–S9), acceptance checks, model tiers, and stops.
2. [System contract](docs/implementation/02-SYSTEM-CONTRACT.md): formulas, thresholds, targets, data rules, spec conflicts and their resolutions.
3. [Operating rules](docs/implementation/03-OPERATING-RULES.md): context checkpoints, models and escalation, Linear, GitHub, compute, subscription.
4. [Current handoff](docs/implementation/HANDOFF.md): the next action and unresolved setup details.
5. [Original assignment](docs/implementation/assignment-original.txt): preserved verbatim.

## Relationship to the July plan

`docs/superpowers/plans/2026-07-04-enron-digital-clone.md` is preserved as the **technical implementation reference**: its Tasks 1–16 map onto stages S1–S9 (mapping stated in each stage). This staged plan **supersedes its execution instructions**: work proceeds stage-by-stage with stops, Linear tracking, and GitHub saves per 03-OPERATING-RULES — not as one long task-by-task run. Where the two documents conflict, 01-STAGES and 02-SYSTEM-CONTRACT win.

## Resources

See [RESOURCES.md](docs/implementation/RESOURCES.md) for the confirmed GitHub account, dataset sources, and the items Stage 0 must still confirm (repo name, Linear project, VS Code model labels, Python version).
