import warnings
warnings.filterwarnings("ignore", message="BigQuery Storage module not found")

import sqlglot
from sqlglot import exp

from src.state import AgentState
from src.config import PII_COLUMNS, MAX_RETRIES
from src.database.bq_client import BigQueryRunner

bq = BigQueryRunner()
from src.console import print_step, print_error


########  Ensureing PII information is not exposed in SQL queries  ########
def validate_sql(sql: str) -> dict:
    """Parse SQL AST with sqlglot and block queries that reference PII columns."""
    parsed = sqlglot.parse_one(sql, dialect="bigquery")
    print_step("SQL Validation", f"Parsed SQL AST:\n{parsed.sql(dialect='bigquery', pretty=True)}")

    # Block SELECT * and table.* but allow COUNT(*) by checking the parent node type
    for star in parsed.find_all(exp.Star):
        if not isinstance(star.parent, exp.Count):
            return {"valid": False, "error": "Wildcard select is not allowed. Select explicit columns only."}

    # Only check the outermost SELECT (what the user actually sees) — CTEs can use PII internally
    AGGREGATES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)
    for column in parsed.expressions:
        for col_ref in column.find_all(exp.Column):
            if col_ref.name.lower() in PII_COLUMNS and not col_ref.find_ancestor(*AGGREGATES):
                return {"valid": False, "error": f"PII column '{col_ref.name}' in SELECT is not allowed."}

    return {"valid": True, "error": ""}


######## SQL Executor Node: Executes SQL and returns sanitized rows ########
def sql_executor(state: AgentState) -> dict:
    """Execute SQL and return sanitized rows."""
    retry_count = state.get("retry_count", 0)
    try:
        validation = validate_sql(state.get("generated_sql", ""))
        if not validation["valid"]:
            raise ValueError(validation["error"])

        df = bq.execute_query(state.get("generated_sql", ""))

        # PII filter
        dropped = [c for c in df.columns if c.lower() in PII_COLUMNS]
        if dropped:
            df = df.drop(columns=dropped)
            print_step("PII Filter", f"[yellow]Removed columns:[/yellow] {dropped}")

        rows = df.to_dict(orient="records")

        # Empty results count as a retry so sql_generator can adjust the query
        if not rows:
            print_error(f"Retry {retry_count + 1}/{MAX_RETRIES}: query returned 0 rows")
            return {"rows": [], "error_message": "Query returned 0 rows, try a broader query.", "retry_count": retry_count + 1}

        return {"rows": rows, "error_message": "", "retry_count": retry_count}

    except Exception as e:
        print_error(f"Retry {retry_count + 1}/{MAX_RETRIES}: {str(e)}")
        return {"error_message": str(e), "retry_count": retry_count + 1, "rows": []}
