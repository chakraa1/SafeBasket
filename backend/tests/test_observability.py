"""Proves the agent emits LangSmith traces even in the free (no-LLM) tier.

We inject a fake LangSmith client that records every run instead of sending it
over the network, enable a tracing context, then run the agent and assert that
the expected spans (agent -> analyze -> match / faiss retrieve) were created.
"""

from __future__ import annotations

from langsmith import Client
from langsmith.run_helpers import tracing_context

from app.config import Settings
from app.core.agent import run_agent


class _RecordingClient(Client):
    """A LangSmith client that captures runs locally instead of uploading."""

    def __init__(self) -> None:
        super().__init__(api_key="test-key", auto_batch_tracing=False)
        self.runs: list[str] = []

    def create_run(self, name, inputs, run_type, **kwargs):  # noqa: D401
        self.runs.append(name)

    def update_run(self, *args, **kwargs):
        pass


def test_free_tier_emits_traces():
    client = _RecordingClient()
    with tracing_context(enabled=True, client=client):
        result = run_agent(brand="Maggi Masala")

    # Free tier => deterministic engine, but the run is still fully traced.
    assert result["engine"] == "rule-based"
    names = client.runs
    assert "safebasket_agent" in names, names
    assert "analyze" in names, names
    assert "match_harmful_ingredients" in names, names
    assert "faiss_rag_retrieve" in names, names


def test_langsmith_config_sets_env(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test-123")
    for var in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING", "LANGCHAIN_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    settings = Settings()
    assert settings.langsmith_enabled
    settings.configure_langsmith()
    import os

    assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
    assert os.environ.get("LANGSMITH_TRACING") == "true"
