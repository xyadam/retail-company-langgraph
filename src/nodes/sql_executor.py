import warnings
warnings.filterwarnings("ignore", message="BigQuery Storage module not found")

from src.state import AgentState
from src.config import PII_COLUMNS, MAX_RETRIES
from src.database.bq_client import BigQueryRunner

bq = BigQueryRunner()
from src.console import print_step, print_error

########  Ensureing PII information is not exposed in SQL queries  ########
def validate_sql(sql: str) -> dict:
    """Validate SQL query. Returns dict with 'valid' bool and 'error' message."""
    lowered = sql.lower()

    if "select *" in lowered or ".*" in lowered:
        return {"valid": False, "error": "Wildcard select is not allowed. Select explicit columns only."}

    for col in PII_COLUMNS:
        if col.lower() in lowered:
            return {"valid": False, "error": f"PII column '{col}' is not allowed."}

    return {"valid": True, "error": ""}


######## SQL Executor Node: Executes SQL and returns sanitized rows ########
def sql_executor(state: AgentState) -> dict:
    """Execute SQL and return sanitized rows."""
    try:
        validation = validate_sql(state["generated_sql"])
        if not validation["valid"]:
            raise ValueError(validation["error"])

        df = bq.execute_query(state["generated_sql"])

        # PII filter
        dropped = [c for c in df.columns if c.lower() in PII_COLUMNS]
        if dropped:
            df = df.drop(columns=dropped)
            print_step("PII Filter", f"[yellow]Removed columns:[/yellow] {dropped}")

        rows = df.to_dict(orient="records")

        # Empty results count as a retry so sql_generator can adjust the query
        if not rows:
            print_error(f"Retry {state['retry_count'] + 1}/{MAX_RETRIES}: query returned 0 rows")
            return {"rows": [], "error_message": "Query returned 0 rows, try a broader query.", "retry_count": state["retry_count"] + 1}

        return {"rows": rows, "error_message": "", "retry_count": state["retry_count"]}

    except Exception as e:
        print_error(f"Retry {state['retry_count'] + 1}/{MAX_RETRIES}: {str(e)}")
        return {"error_message": str(e), "retry_count": state["retry_count"] + 1, "rows": []}
