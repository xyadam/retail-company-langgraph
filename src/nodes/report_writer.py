import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AgentState
from config import llm
from config import load_persona


def report_writer(state: AgentState) -> dict:
    """Format query rows into an executive report."""
    persona = load_persona()

    # If all retries failed, tell the user
    if state["error_message"]:
        content = f"I couldn't retrieve the data. Try rephrasing your question.\nError: {state['error_message']}"
        return {"final_report": content, "messages": [AIMessage(content=content)]}

    # Ask LLM to write executive report from the query results
    resp = llm.invoke([
        SystemMessage(content=(
            f"You are a data analyst writing reports for retail executives.\n"
            f"Tone: {persona['tone']}\n"
            f"Style: {persona['report_style']}\n"
            f"NEVER include any PII (names, emails, addresses) in your report.\n"
            f"Start with: {persona['greeting']}"
        )),
        HumanMessage(content=(
            f"Question: {state['user_question']}\n\n"
            f"Query results (JSON):\n{json.dumps(state['rows'], default=str)}\n\n"
            f"Write a concise executive report answering the question from this data."
        )),
    ])
    return {"final_report": resp.content, "messages": [AIMessage(content=resp.content)]}
