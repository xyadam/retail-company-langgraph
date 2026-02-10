"""
Alternative report writer using LangChain create_agent() with PIIMiddleware.
This is NOT wired into the graph. It demonstrates how PII masking could be
handled via LangChain's built-in middleware for free-text scanning, as an
alternative to the column-level filtering used in pii_filter.py.

PII strategy:
- Emails: PIIMiddleware with "redact" catches email patterns in AI output
- Names: LLM system prompt instructs to never include names (names are too
  diverse for regex - cultural variations, compound names, non-Latin chars)
"""
import json
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from state import AgentState
from config import llm, load_persona


###########################################################################
##                    AGENT WITH PII MIDDLEWARE
###########################################################################

report_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=(
        "You are a data analyst writing reports for retail executives. "
        "Write a concise executive report from the provided data. "
        "NEVER include any person names, emails, or addresses in your report. "
        "Replace any person names with generic labels like 'Customer 1', 'Customer 2', etc. "
        "This is EXTREMELY IMPORTANT for privacy compliance."
    ),
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_output=True),
    ],
    checkpointer=InMemorySaver(),
)


###########################################################################
##                     NODE FUNCTION
###########################################################################

def report_writer_pii_agent(state: AgentState) -> dict:
    """Write executive report using LangChain agent with PII middleware."""
    persona = load_persona()

    if state["error_message"]:
        content = f"I couldn't retrieve the data. Try rephrasing your question.\nError: {state['error_message']}"
        return {"final_report": content, "messages": [AIMessage(content=content)]}

    config = {"configurable": {"thread_id": "report"}}
    result = report_agent.invoke(
        {"messages": [{"role": "user", "content": (
            f"Tone: {persona['tone']}\n"
            f"Style: {persona['report_style']}\n"
            f"Start with: {persona['greeting']}\n\n"
            f"Question: {state['user_question']}\n\n"
            f"Query results (JSON):\n{json.dumps(state['rows'], default=str)}\n\n"
            f"Write a concise executive report answering the question from this data. Only include the report in your response. If the data doesn't answer the question, say so and don't make up an answer."
        )}]},
        config,
    )

    content = result["messages"][-1].content
    return {"final_report": content, "messages": [AIMessage(content=content)]}
