import json
from config import SRC
from state import AgentState


def golden_knowledge(state: AgentState) -> dict:
    """Load golden knowledge examples into state for SQL generation."""
    with open(SRC / "golden_knowledge" / "golden_knowledge.json", "r", encoding="utf-8") as f:
        examples = json.load(f)
    formatted = [f"Q: {ex['question']}\nSQL: {ex['sql']}\nReport: {ex['report']}" for ex in examples]
    return {"golden_examples": "\n\n".join(formatted)}
