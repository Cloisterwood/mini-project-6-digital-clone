"""Tests for the optional CrewAI mapping (July Task 15).

`describe_crew` must work fully offline (the graded pipeline is deterministic);
`build_crew` must refuse to build a live crew without OPENAI_API_KEY.
"""
import pytest

from digital_clone.crew import describe_crew


def test_crew_describes_five_agents():
    agents = describe_crew()
    assert len(agents) == 5
    roles = {a["role"] for a in agents}
    assert roles == {"ChatStyleAgent", "RAGAgent", "EvaluatorAgent",
                     "FallbackAgent", "PlannerAgent"}
    assert all(a["goal"] and a["backstory"] for a in agents)


def test_build_crew_requires_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from digital_clone.crew import build_crew
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        build_crew(planner=None)


def test_build_crew_module_imports_without_crewai_installed():
    # The module must import (and describe_crew must run) on interpreters
    # where crewai itself cannot be installed (e.g. Python 3.14): the heavy
    # crewai import lives inside build_crew, not at module level.
    import digital_clone.crew as crew_module
    assert callable(crew_module.describe_crew)
    assert callable(crew_module.build_crew)
