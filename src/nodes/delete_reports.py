from langgraph.types import interrupt

from src.state import AgentState
from src.console import print_step


SAVED_REPORTS = ["Q1 Revenue Analysis", "Top Customers 2025", "Category Breakdown"]


def delete_reports(state: AgentState) -> dict:
    """Destructive action with human confirmation via interrupt."""
    answer = interrupt(f"About to delete {len(SAVED_REPORTS)} report(s). Confirm? (yes/no)")

    if answer.lower() != "yes":
        return {"final_report": "Deletion cancelled."}

    deleted_count = len(SAVED_REPORTS)
    SAVED_REPORTS.clear()
    print_step("Delete", f"Deleted {deleted_count} reports")
    return {"final_report": f"Deleted {deleted_count} report(s)."}
