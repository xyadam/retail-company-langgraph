from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.config import MAX_RETRIES
from src.nodes import (
    router, golden_knowledge, sql_generator, sql_executor,
    report_writer, general_response,
)


###########################################################################
##                       CONDITIONAL EDGES
###########################################################################

def route_by_intent(state: AgentState) -> str:
    if state.get("intent") == "general":
        return "general_response"
    return "golden_knowledge"


def route_after_execution(state: AgentState) -> str:
    if state.get("error_message") and state.get("retry_count", 0) < MAX_RETRIES:
        return "sql_generator"
    return "report_writer"


###########################################################################
##                         BUILD GRAPH
###########################################################################

workflow = StateGraph(AgentState)

workflow.add_node("router", router)
workflow.add_node("golden_knowledge", golden_knowledge)
workflow.add_node("sql_generator", sql_generator)
workflow.add_node("sql_executor", sql_executor)
workflow.add_node("report_writer", report_writer)
workflow.add_node("general_response", general_response)

workflow.add_edge(START, "router")

workflow.add_conditional_edges("router", route_by_intent, {
    "golden_knowledge": "golden_knowledge",
    "general_response": "general_response",
})

workflow.add_edge("golden_knowledge", "sql_generator")
workflow.add_edge("sql_generator", "sql_executor")
workflow.add_conditional_edges("sql_executor", route_after_execution, {
    "sql_generator": "sql_generator",
    "report_writer": "report_writer",
})

workflow.add_edge("report_writer", END)
workflow.add_edge("general_response", END)


# Chekcpointer is not necessary because langgraph dev provides it its
# own in-memory checkpointer for development purposes.
graph = workflow.compile()
