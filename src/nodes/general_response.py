from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AgentState
from config import llm


def general_response(state: AgentState) -> dict:
    """Handle non-data questions."""
    recent = "\n".join(f"{m.type}: {m.content}" for m in state["messages"][-6:])

    resp = llm.invoke([
        SystemMessage(content=(
            "You are a helpful retail data analysis assistant.\n"
            "You can answer questions about the database schema (orders, order_items, products, users),\n"
            "explain your capabilities, or have general conversation.\n"
            "Keep responses concise.\n"
            f"Recent conversation:\n{recent}"
        )),
        HumanMessage(content=state["user_question"]),
    ])
    return {"final_report": resp.content, "messages": [AIMessage(content=resp.content)]}
