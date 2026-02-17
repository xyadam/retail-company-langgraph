from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


###########################################################################
##                             STATE
###########################################################################

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str
    intent: str
    golden_examples: str
    generated_sql: str
    rows: list
    error_message: str
    retry_count: int
    final_report: str


MAX_RETRIES = 3


###########################################################################
##                         PLACEHOLDER NODES
###########################################################################

def router(state: AgentState) -> AgentState:
    """Classifies user intent as data_query, general, or delete using LLM."""
    return state


def golden_knowledge(state: AgentState) -> AgentState:
    """Loads golden knowledge few-shot examples (Q->SQL->Report trios)
    from the Golden Knowledge bucket into state for SQL generation."""
    return state


def sql_generator(state: AgentState) -> AgentState:
    """Generates BigQuery SQL from user question + schema + golden examples.
    On retry: receives error_message for self-correction."""
    return state


def sql_executor(state: AgentState) -> AgentState:
    """Executes SQL via BigQueryRunner. Filters PII columns from results.
    On error: stores error_message, increments retry_count."""
    return state


def report_writer(state: AgentState) -> AgentState:
    """Formats query results into executive report using persona.yaml tone.
    On error path: generates graceful failure message."""
    return state


def general_response(state: AgentState) -> AgentState:
    """Handles non-data questions: schema info, greetings, capabilities."""
    return state


def delete_reports(state: AgentState) -> AgentState:
    """Mock report deletion with interrupt() confirmation flow.
    High-stakes oversight: requires user confirmation before destructive action."""
    return state


###########################################################################
##                       CONDITIONAL EDGES
###########################################################################

def route_by_intent(state: AgentState) -> str:
    if state.get("intent") == "general":
        return "general_response"
    if state.get("intent") == "delete":
        return "delete_reports"
    return "golden_knowledge"


def route_after_execution(state: AgentState) -> str:
    """Self-correction loop: retry up to 3x on SQL errors."""
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
workflow.add_node("delete_reports", delete_reports)

workflow.add_edge(START, "router")

workflow.add_conditional_edges("router", route_by_intent, {
    "golden_knowledge": "golden_knowledge",
    "general_response": "general_response",
    "delete_reports": "delete_reports",
})

workflow.add_edge("golden_knowledge", "sql_generator")
workflow.add_edge("sql_generator", "sql_executor")
workflow.add_conditional_edges("sql_executor", route_after_execution, {
    "sql_generator": "sql_generator",
    "report_writer": "report_writer",
})

workflow.add_edge("report_writer", END)
workflow.add_edge("general_response", END)
workflow.add_edge("delete_reports", END)

graph = workflow.compile()

output_path = r"C:\Users\xyada\Desktop\retail-company-langgraph\docs\current_project\langgraph_flow.png"
graph.get_graph().draw_mermaid_png(output_file_path=output_path)
print(f"Graph saved to: {output_path}")
