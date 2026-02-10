from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from config import llm, load_db_schema
from console import print_sql

schema_text = load_db_schema()


def sql_generator(state: AgentState) -> dict:
    """Generate a BigQuery SQL query from the user's question."""
    
    # Build context from recent conversation and any previous error
    history = "\n".join(f"{m.type}: {m.content}" for m in state["messages"][-6:])
    error_context = f"\nPrevious SQL failed with: {state['error_message']}\nFix the error.\n" if state.get("error_message") else ""
    examples_text = state.get("golden_examples", "")

    # Ask LLM to generate SQL
    resp = llm.invoke([
        SystemMessage(content=(
            "You are a BigQuery SQL expert for a retail ecommerce database.\n"
            "Generate a single SQL query. Return ONLY the SQL, no markdown.\n\n"
            "RULES:\n"
            "- Fully qualified tables: `bigquery-public-data.thelook_ecommerce.TABLE`\n"
            "- NEVER select PII columns: first_name, last_name, email, street_address\n"
            "- No total column on orders - SUM order_items.sale_price instead\n"
            "- When asked for 'most', 'best', 'top' without a number, default to LIMIT 10 for richer context\n"
            f"- Current date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"CONVERSATION:\n{history}\n\n"
            f"SCHEMA:\n{schema_text}\n\n"
            f"GOLDEN KNOWLEDGE EXAMPLES:\n{examples_text}"
            f"{error_context}"
        )),
        HumanMessage(content=state["user_question"]),
    ])

    # Strip markdown fences if LLM wraps the SQL
    sql = resp.content.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
    print_sql(sql)
    return {"generated_sql": sql, "error_message": ""}
