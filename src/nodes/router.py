from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from state import AgentState
from config import llm
from console import print_step


class RouteIntent(BaseModel):
    intent: Literal["data_query", "general"]


def router(state: AgentState) -> dict:
    """Classify intent as data_query or general."""
    structured_llm = llm.with_structured_output(RouteIntent)

    result = structured_llm.invoke([
        SystemMessage(content=(
            "You classify user questions for a retail data analysis system.\n"
            "The system has access to: orders, order_items, products, and users tables "
            "(sales, revenue, customers, countries, categories, brands, time-based metrics).\n"
            "Any question about data, numbers, sales, customers, products, trends, or analysis = data_query.\n"
            "Only greetings, small talk, or 'what can you do' type questions = general."
        )),
        HumanMessage(content=state["user_question"]),
    ])

    print_step("Router", f"Intent: [bold]{result.intent}[/bold]")
    return {"intent": result.intent}
