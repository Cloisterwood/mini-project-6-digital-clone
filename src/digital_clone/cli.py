"""Interactive digital-clone demo. Requires artifacts built by
scripts/build_style_profile.py and scripts/build_knowledge_base.py."""
import argparse

from digital_clone.agents.planner_agent import build_planner
from digital_clone.config import CloneConfig
from digital_clone.models import CloneResponse


def render(result: CloneResponse) -> str:
    lines = [f"\n--- query: {result.query}"]
    if result.evaluation:
        e = result.evaluation
        lines.append(f"scores: style={e.style_score:.2f} grounded={e.groundedness_score:.2f} "
                     f"confidence={e.confidence_score:.2f} final={e.final_score:.2f} "
                     f"-> {e.decision.upper()}")
    if result.delivered:
        lines.append(result.response_text)
    else:
        fb = result.fallback
        lines.append(f"[FALLBACK: {fb.trigger_reason}]")
        lines.append(fb.context_summary)
        lines.append(f"Book here: {fb.calendar_link}")
        lines.append("Available slots: " + ", ".join(fb.available_slots))
    lines.append(f"(latency: {result.latency_seconds * 1000:.0f} ms)")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enron digital clone demo")
    parser.add_argument("--query", help="one-shot query (otherwise interactive)")
    args = parser.parse_args()

    print("Loading agents (embedding model may take a few seconds)...")
    planner = build_planner(CloneConfig())
    print("Ready. 5-agent digital clone online.")

    if args.query:
        print(render(planner.process(args.query)))
        return
    while True:
        try:
            query = input("\nAsk the clone (or 'quit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in {"quit", "exit", ""}:
            break
        print(render(planner.process(query)))


if __name__ == "__main__":
    main()
