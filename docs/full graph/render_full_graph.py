"""
Full System Architecture Graph (HLD)

Starting point: our LIVE prototype graph (router -> sql_generator -> sql_executor -> report_writer)
Extended with all 8 TODO requirements as they would be implemented in production.

Requirements mapping:
  Req 1 - Hybrid Intelligence:     golden_examples (semantic search on golden knowledge)
  Req 2 - PII Masking:             Built into sql_executor (column-level) + PIIMiddleware on report_writer
  Req 3 - High-Stakes Oversight:   report_manager -> delete_confirmation -> delete_executor
  Req 4 - Learning Loop:           user_preferences_loader (user-level) + interaction_logger (system-level)
  Req 5 - Resilience:              sql_executor -> retry loop back to sql_generator (LIVE)
  Req 6 - Quality Assurance:       sql_validator (LLM checks SQL matches intent before execution)
  Req 7 - Logging:                 interaction_logger (metrics, errors, latency tracking)
  Req 8 - Persona Management:      persona config loaded in report_writer from persona.yaml (LIVE)
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


###########################################################################
##                             STATE
###########################################################################

class FullSystemState(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str
    intent: str                 # data_query | general | report_action

    # Data query path
    golden_examples: str        # Req 1: retrieved similar trios
    generated_sql: str
    sql_validation: str         # Req 6: "valid" | "mismatch"
    query_result: str
    error_message: str
    retry_count: int

    # Report path
    user_preferences: dict      # Req 4: user-level preferences (tables vs bullets)
    confirmation: str           # Req 3: "yes" | "no" for destructive ops

    # Output
    final_report: str


###########################################################################
##                    LIVE SYSTEM NODES (implemented)
###########################################################################

def router(state: FullSystemState) -> FullSystemState:
    """Classifies intent: data_query | general | report_action
    Uses LLM with structured output (Pydantic Literal field)."""
    return state


def sql_generator(state: FullSystemState) -> FullSystemState:
    """Generates BigQuery SQL from question + schema + golden examples.
    On retry: receives error_message for self-correction. (Req 5: LIVE)"""
    return state


def sql_executor(state: FullSystemState) -> FullSystemState:
    """Executes SQL via BigQueryRunner. (Req 5: LIVE)
    - Validates no SELECT * or PII columns in SQL (Req 2: LIVE)
    - Hard-drops PII columns from results via pandas (Req 2: LIVE)
    - On error: stores error_message, increments retry_count for retry loop"""
    return state


def report_writer(state: FullSystemState) -> FullSystemState:
    """Formats results into executive report. (Req 8: LIVE)
    - Loads persona.yaml for tone/style (non-devs can edit without deploy)
    - LLM instructed to never include PII (Req 2: defense-in-depth)
    - PIIMiddleware on output catches leaked emails (Req 2: LIVE alternative)
    - Applies user_preferences for format (Req 4)"""
    return state


def general_response(state: FullSystemState) -> FullSystemState:
    """Handles non-data questions: schema info, greetings, capabilities."""
    return state


###########################################################################
##                  FULL SYSTEM EXTENSION NODES
###########################################################################

def golden_examples(state: FullSystemState) -> FullSystemState:
    """Req 1 (Hybrid Intelligence): Semantic similarity search on
    Golden Knowledge bucket. Retrieves top-k Q->SQL->Report trios
    to use as few-shot examples for sql_generator.
    (LIVE uses static file load; production would use vector search)"""
    return state


def sql_validator(state: FullSystemState) -> FullSystemState:
    """Req 6 (Quality Assurance): LLM reviews generated SQL against
    user intent BEFORE execution. Catches semantic mismatches
    (e.g. query returns revenue when user asked for order count).
    Returns 'valid' or 'mismatch' to route accordingly."""
    return state


def user_preferences_loader(state: FullSystemState) -> FullSystemState:
    """Req 4 (Learning Loop - User Level): Loads user-specific preferences
    (tables vs bullets, detail level) from persistent storage.
    Injected into report_writer prompt for personalized output."""
    return state


def report_manager(state: FullSystemState) -> FullSystemState:
    """Req 3 (High-Stakes Oversight): Manages saved reports library.
    Supports save/list/search operations on reports."""
    return state


def delete_confirmation(state: FullSystemState) -> FullSystemState:
    """Req 3 (High-Stakes Oversight): Human-in-the-loop interrupt.
    Asks user to explicitly confirm destructive delete before execution.
    Uses LangGraph interrupt() for GDPR compliance flow."""
    return state


def delete_executor(state: FullSystemState) -> FullSystemState:
    """Req 3: Executes report deletion ONLY after user confirmation."""
    return state


def interaction_logger(state: FullSystemState) -> FullSystemState:
    """Req 7 (Logging) + Req 4 (Learning Loop - System Level):
    Logs: query, generated SQL, result, latency, error count,
    PII blocks, retry count, user feedback.
    Feeds back into golden knowledge for continuous improvement."""
    return state


###########################################################################
##                       CONDITIONAL EDGES
###########################################################################

def route_by_intent(state: FullSystemState) -> str:
    intent = state.get("intent", "")
    if intent == "general":
        return "general_response"
    if intent == "report_action":
        return "report_manager"
    return "golden_examples"


def route_after_validation(state: FullSystemState) -> str:
    """Req 6: If SQL doesn't match user intent, loop back to regenerate."""
    if state.get("sql_validation") == "mismatch":
        return "sql_generator"
    return "sql_executor"


def route_after_execution(state: FullSystemState) -> str:
    """Req 5: Self-correction loop - retry up to 3x on SQL errors."""
    if state.get("error_message") and state.get("retry_count", 0) < 3:
        return "sql_generator"
    return "user_preferences_loader"


def route_report_action(state: FullSystemState) -> str:
    """Req 3: Destructive delete requires confirmation flow."""
    if "delete" in state.get("user_question", "").lower():
        return "delete_confirmation"
    return "interaction_logger"


def route_after_confirmation(state: FullSystemState) -> str:
    """Req 3: Execute delete or cancel based on user response."""
    if state.get("confirmation") == "yes":
        return "delete_executor"
    return "interaction_logger"


###########################################################################
##                         BUILD FULL GRAPH
###########################################################################

workflow = StateGraph(FullSystemState)

# ---- Nodes ----
workflow.add_node("router", router)
workflow.add_node("golden_examples", golden_examples)
workflow.add_node("sql_generator", sql_generator)
workflow.add_node("sql_validator", sql_validator)
workflow.add_node("sql_executor", sql_executor)
workflow.add_node("user_preferences_loader", user_preferences_loader)
workflow.add_node("report_writer", report_writer)
workflow.add_node("general_response", general_response)
workflow.add_node("report_manager", report_manager)
workflow.add_node("delete_confirmation", delete_confirmation)
workflow.add_node("delete_executor", delete_executor)
workflow.add_node("interaction_logger", interaction_logger)

# ---- Entry ----
workflow.add_edge(START, "router")

# ---- Router: 3 intent branches ----
workflow.add_conditional_edges("router", route_by_intent, {
    "golden_examples": "golden_examples",
    "general_response": "general_response",
    "report_manager": "report_manager",
})

# ---- Data query path (core pipeline) ----
# golden_examples -> sql_generator -> sql_validator -> sql_executor
workflow.add_edge("golden_examples", "sql_generator")
workflow.add_edge("sql_generator", "sql_validator")

# Req 6: QA validation can loop back to sql_generator
workflow.add_conditional_edges("sql_validator", route_after_validation, {
    "sql_generator": "sql_generator",
    "sql_executor": "sql_executor",
})

# Req 5: Execution can retry (back to sql_generator) or continue
workflow.add_conditional_edges("sql_executor", route_after_execution, {
    "sql_generator": "sql_generator",
    "user_preferences_loader": "user_preferences_loader",
})

# Req 4: Load user preferences -> report_writer -> logger
workflow.add_edge("user_preferences_loader", "report_writer")
workflow.add_edge("report_writer", "interaction_logger")

# ---- General chat path ----
workflow.add_edge("general_response", "interaction_logger")

# ---- Report management path (Req 3: destructive ops) ----
workflow.add_conditional_edges("report_manager", route_report_action, {
    "delete_confirmation": "delete_confirmation",
    "interaction_logger": "interaction_logger",
})

workflow.add_conditional_edges("delete_confirmation", route_after_confirmation, {
    "delete_executor": "delete_executor",
    "interaction_logger": "interaction_logger",
})

workflow.add_edge("delete_executor", "interaction_logger")

# ---- All paths converge at logger -> END ----
workflow.add_edge("interaction_logger", END)

# ---- Compile and render ----
graph = workflow.compile()

output_path = r"C:\Users\xyada\Desktop\opsfleet langgraph\docs\full graph\full_system_langgraph.png"
graph.get_graph().draw_mermaid_png(output_file_path=output_path)
print(f"Full system graph saved to: {output_path}")
