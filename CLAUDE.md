# OpsFleet Data Analysis Chat Agent

## Detailed TODOD given by the company for this project:
<project_descrption>
## The Challenge: Design and Build a Data Analysis Chat Assistant

You are building an internal data agent for a Retail Company's non-technical executive team (Store and Regional Managers). These managers need to ask complex questions about sales, inventory, and performance (e.g., "Why is the Tel Aviv branch underperforming?")
The agent will have access to:

- The Database: A read-only connection to a SQL database containing raw transaction logs.
- The "Golden Knowledge" Bucket: A data lake containing historical "Trios" (Question → SQL Query → Analyst Report) created by human experts.

**The Task:** Design the full system (HLD) and build a prototype that allows executives to query this data naturally.

### Requirements:

1. **Hybrid Intelligence:** The agent cannot rely on SQL alone. It must use the "Golden Bucket" to understand *how* analysts previously interpreted questions and apply similar logic to new queries.
2. **Safety & PII Masking:** The raw transaction logs contain Customer Names and Emails. The agent is **strictly forbidden** from displaying this PII in the final output, even if the SQL query retrieves it.
3. **High-Stakes Oversight (Destructive Ops):** While the DB is read-only, the agent manages a "Saved Reports" library. The agent must support commands like *"Delete all reports mentioning Client X"* (GDPR compliance). This is a destructive action and requires a strict confirmation flow before execution.
4. **Continuous Improvement (The Learning Loop):**
   1. **User Level:** The agent should remember that "Manager A" prefers tables while "Manager B" prefers bullet points.
   2. **System Level:** The agent should be able to learn from past interactions.
5. **Resilience & Graceful Error Handling:** The system must detect SQL syntax errors or empty returns and attempt to **self-correct** before giving up, without crashing the user interface and without inflating costs.
6. **Quality Assurance:** How do you evaluate the agent before deployment? Specifically, how do you verify that the generated SQL actually answers the user's intent?
7. **Logging:** We need to know when the agent is failing and why. Define the metrics you would track and how you would support deep dive analysis.
8. **Agility (Persona Management):** The CEO wants to change the "tone" of the reports weekly. The system must allow non-developers to update the agent's instructions without a code deployment.

###  Deliverables:

1. **Architecture Diagram (Mermaid etc):** Highlighting the building blocks and flow of the system based on the requirements above. In case you are planning to use a framework for one of the building blocks, specify which one.
2. **Brief technical explanation covering:**
   1. Reasoning for the chosen Cloud services / LLM models / frameworks used.
   2. Data flow between components (if needs to elaborate on HLD).
   3. Error handling and fallback strategies.
   4. Setup Instructions and example run
3.  **Working Code/Prototype:** Build a chat **agent** that can generate and run SQL queries against the DB listed below and create a report. The prototype needs to support 2 of the following requirements (defined above):
   1. Safety & PII Masking
   2. High-Stakes Oversight
   3. Resilience & Graceful Error Handling
   4. Quality Assurance
   5. Logging
4. **Simple** CLI-based interface for chat interactions. (UI's won't gain any additional points)
5. **Your solution must be runnable on another machine (Docker is not a must, just proper setup instructions).**
6. Use a framework of your choice (preferably **Lang Graph / Lang Chain V1**)

**Note: the prototype needs to be simple. Points will be redacted for overengineering and bloated code bases.**
Our assessment will focus mainly on system design and an elegant Prototype

### Dataset Specification:

- **Dataset:** `bigquery-public-data.thelook_ecommerce`
- **Required Tables:**
  - `orders` - Customer order information
  - `order_items` - Individual items within orders
  - `products` - Product catalog and details
  - `users` - Customer demographics and information

### Expected Agent Capabilities:

### Your p**rototype** agent should be able to perform data analysis and generate insights such as:

- Customer behavior (e.g., top customers, total spend)
- Product performance
- Time-based metrics (e.g., monthly revenue, up-to-date revenue by product)
- Answer questions about the general structure of the database

1. **Use BigQuery integration** to query and analyze the specified tables. Your agent should be able to construct and execute SQL queries dynamically based on the analysis requirements.
2. You should preferably use one of the newer **Google Gemini models**. You can get a free API key from [Google AI Studio](https://aistudio.google.com/apikey). Please be mindful of the [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits). Alternatively, you can use OpenRouter or Ollama if you prefer (or have issues with rate limits) . We have created a simple client for your convenience:  https://github.com/Opsfleet/lc-openrouter-ollama-client

### Setup Instructions

Environment Setup

1. **Install Python dependencies:**

```
pip install -r requirements.txt
```

GCP/BigQuery Setup

1. **Set up BigQuery access** by following the [BigQuery Client Libraries documentation](https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python) if you don't already have BigQuery access configured.
2. **Free Tier:** Google Cloud provides 1TB of free BigQuery compute per month, which is more than sufficient for this challenge.
3. **Authentication:** Ensure your environment is authenticated with Google Cloud to access the public datasets.

------

## Time Expectation

We expect this assignment to take between 6 to 12 hours of work.

## Submission

Share (make it public or invite us with our emails) with us a **your Git repository** (GitHub, GitLab, etc) with:

- Documentation
- Source code
- Architecture diagram

------

## Resources

### **Quick Starts**

- https://docs.langchain.com/oss/python/langchain/quickstart
- https://docs.langchain.com/oss/python/langgraph/quickstart
- https://docs.langchain.com/oss/python/langgraph/add-memory
</project_description>



## Project Purpose

Internal data agent for a Retail Company's non-technical executive team. Managers ask natural language questions about sales, inventory, and performance. The agent generates SQL, queries BigQuery, and returns executive reports.

**Assignment requirements:** Pick 2 of 5 features for prototype. We implement:
1. **Safety & PII Masking** - Never display customer PII (names, emails) in output
2. **Resilience & Self-Correction** - Retry failed SQL queries with fixes (max 3 attempts)

---

## Project Structure

```
src/
├── main.py                          # CLI entry point (input loop)
├── graph.py                         # LangGraph definition (nodes, edges, state)
├── state.py                         # AgentState TypedDict
├── config.py                        # Constants, paths, helper functions
├── console.py                       # Rich console helpers (print_step, print_sql, print_report)
├── database/
│   ├── bq_client.py                 # BigQuery client (PROVIDED)
│   └── db_schema.md                 # Database schema reference
├── nodes/
│   ├── __init__.py                  # Re-exports all node functions
│   ├── shared.py                    # LLM, BQ client, schema (shared instances)
│   ├── router.py                    # Classify intent (query vs general)
│   ├── golden_knowledge.py          # Load golden knowledge few-shot examples into state
│   ├── sql_generator.py             # Generate SQL from question + schema + golden examples
│   ├── sql_executor.py              # Run SQL via BigQueryRunner, return markdown or error
│   ├── pii_filter.py                # Drop PII columns, collect result into collected_data
│   ├── report_writer.py             # Format final response for user
│   └── general_response.py          # Handle non-data questions
├── golden_knowledge/
│   └── golden_knowledge.json        # Few-shot examples (Question -> SQL -> Report)
├── persona/
│   └── persona.yaml                 # Editable report tone/style (Requirement 8: Agility)
└── questions/
    └── test_questions.md            # 7 curated test questions with expected behavior
```

---

## Architecture

```
User Question
      │
      ▼
┌─────────────┐
│   Router    │ ─── General question ──► Direct LLM response
└─────────────┘
      │ Data question
      ▼
┌──────────────────┐
│ Golden Knowledge │  Loads few-shot examples (Q->SQL->Report trios)
└──────────────────┘
      │
      ▼
┌──────────────┐
│ SQL Generator│ ◄── Schema + Golden Examples + collected_data from prior turns
└──────────────┘
      │
      ▼
┌──────────────┐     ┌──────────────┐
│ SQL Executor  │────►│ Error → Retry │ (up to 3x back to SQL Generator)
└──────────────┘     └───────────────┘
      │ Success
      ▼
┌──────────────┐
│  PII Filter  │  Drops PII columns, appends to collected_data
└──────────────┘
      │ (increments query_count)
      │
      ├── query_count < 4 ──► back to SQL Generator (iterative research)
      │
      └── query_count >= 4 ──► Report Writer (synthesize all collected data)
                                      │
                                      ▼
                                   Response
```

---

## Key Components

### 1. State (TypedDict)

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str
    intent: str
    golden_examples: str        # Few-shot examples from golden knowledge bucket
    generated_sql: str
    query_result: str           # Current query result (markdown)
    collected_data: list        # All query results accumulated across research turns
    query_count: int            # How many queries have been run this turn
    error_message: str
    retry_count: int
    final_report: str
```

### 2. PII Masking (pii_filter node)

Blocked columns (from `users` table):
- `email`, `first_name`, `last_name`, `street_address`

City, state, country, postal_code are allowed for grouping/filtering (not personal PII).
Defense in depth: SQL Generator prompt avoids PII + `pii_filter` node drops PII columns from results using pandas.

### 3. Self-Correction Loop

```
SQL Executor
    │
    ├── Success → PII Filter → Collect Result
    │
    └── Error → retry_count < 3?
                    │
                    ├── Yes → SQL Generator (with error context)
                    │
                    └── No → Report Writer (apologize, explain failure)
```

### 4. Golden Knowledge Node

The `golden_knowledge` node is a dedicated graph node that loads few-shot examples from the Golden Knowledge bucket into state. It runs once per data query (after router, before sql_generator). On retry loops, the examples are already in state so the node is bypassed.

File: `src/golden_knowledge/golden_knowledge.json`

Contains 5-10 example trios:
```json
{
  "question": "What are our top 5 products by revenue?",
  "sql": "SELECT p.name, SUM(oi.sale_price) as revenue FROM `bigquery-public-data.thelook_ecommerce.order_items` oi JOIN `bigquery-public-data.thelook_ecommerce.products` p ON oi.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 5",
  "report": "Top 5 products by revenue: 1. Product X ($50K)..."
}
```

The node loads the JSON, formats the examples, and stores them in `state["golden_examples"]`. The `sql_generator` reads from state to inject them into the SQL generation prompt.

### 5. Iterative Research Loop (up to MAX_QUERIES_PER_TURN queries)

Instead of running a single query, the graph loops up to `MAX_QUERIES_PER_TURN` (4) times:
1. SQL Generator creates a query (seeing all previously collected data)
2. SQL Executor runs it
3. PII Filter drops PII columns and appends cleaned result to `collected_data`
4. If `query_count < 4`, loop back to SQL Generator for the next query
5. When done, Report Writer synthesizes all collected data into one report

The SQL Generator sees all prior results, so each subsequent query builds on what was already discovered.
This enables richer analysis — e.g. first query finds the top city, second compares top 10, third checks category breakdown, fourth looks at trends.

### 6. Persona Management (Requirement 8: Agility)

File: `src/persona/persona.yaml`

```yaml
tone: "professional and concise"
report_style: "Use bullet points. Keep insights actionable for store managers."
greeting: "Here's your analysis:"
```

Loaded at runtime by `report_writer` node and injected into the report generation prompt.
Non-developers (e.g. CEO) can edit this YAML file to change report tone weekly without code deployment.
This is a lightweight implementation that demonstrates the concept — in production, this would be a shared config in cloud storage or an admin UI.

---

## BigQuery Dataset

**Dataset:** `bigquery-public-data.thelook_ecommerce`
**Full schema:** `src/db_schema.md`

**Tables (verified):**
- `orders` - order_id, user_id, status, gender, created_at, returned_at, shipped_at, delivered_at, num_of_item
- `order_items` - id, order_id, user_id, product_id, inventory_item_id, status, created_at, shipped_at, delivered_at, returned_at, sale_price
- `products` - id, cost, category, name, brand, retail_price, department, sku, distribution_center_id
- `users` - id, first_name*, last_name*, email*, age, gender, state*, street_address*, postal_code*, city*, country*, latitude, longitude, traffic_source, created_at, user_geom

**PII columns (marked with *):** first_name, last_name, email, street_address (hard-blocked from output)

**Row counts:** orders 125K, order_items 182K, products 29K, users 100K

**Joins:** orders.user_id->users.id, order_items.order_id->orders.order_id, order_items.product_id->products.id

**Data notes:**
- One order has multiple order_items (1:N). No `total` column on orders - sum `order_items.sale_price` to get order total.
- Heavy denormalization: `orders.gender` is a copy of `users.gender`, `order_items.user_id/status/shipped_at/delivered_at/returned_at` are copies from `orders`. The LLM can often query `order_items` alone without joining.

---

## Tech Stack

- **LangGraph** - Agent orchestration (nodes, edges, state, cycles)
- **LangChain** - Model abstraction, tool decorators
- **Gemini 2.5 Flash** - LLM (via `langchain-google-genai`)
- **BigQuery** - Data warehouse (via provided `BigQueryRunner`)
- **CLI** - Simple `input()` loop (no UI needed)
- **MemorySaver** - In-memory checkpointer for conversation continuity across turns

---

## Environment Variables

```
GOOGLE_API_KEY_PAID    # Gemini API key
GOOGLE_CLOUD_PROJECT   # GCP project for BigQuery (optional, uses default)
```

---

## Running the Agent

```bash
cd "C:\Users\xyada\Desktop\opsfleet langgraph"
uv run python src/main.py
```

---

## Testing Commands

Example questions to test:
- "What are the top 5 products by revenue?"
- "How many orders were placed last month?"
- "Which customers spent the most?" (should NOT show names/emails)
- "What is the average order value by country?"
- "Show me user emails" (should refuse or mask)

---

## Files Provided

- `src/database/bq_client.py` - BigQueryRunner class (execute_query, get_table_schema)
- `requirements.txt` - Dependencies (langgraph, langchain-google-genai, google-cloud-bigquery, pandas)
- `TODO.md` - Assignment specification

---

### 6. Conversation Memory (MemorySaver Checkpointer)

The graph compiles with `MemorySaver()` checkpointer and each `invoke()` uses a `thread_id`.
This means the graph ends after each response (START → ... → END), but LangGraph persists
the conversation state (messages history) between invocations automatically.

The CLI loop in `main.py` invokes the graph per question with the same `thread_id`, so
follow-up questions work naturally (e.g. "top products by revenue" → "break that down by month").

```python
from langgraph.checkpoint.memory import MemorySaver

graph = workflow.compile(checkpointer=MemorySaver())
# Each invoke reuses thread_id for conversation continuity
result = graph.invoke({"user_question": q}, config={"configurable": {"thread_id": "1"}})
```

No database, no persistence across restarts — appropriate for a prototype CLI chat.

---

## Implementation Notes

1. **Keep it simple** - Assignment warns against over-engineering
2. **Defense in depth for PII** - System prompt tells LLM to avoid PII + hard filter on results
3. **Retry with context** - On SQL error, pass error message to LLM for fix
4. **Graceful failure** - After 3 retries, apologize and suggest rephrasing
5. **Logging** - Print SQL queries and errors to console for debugging
6. **Persona via YAML** - report_writer loads persona.yaml at runtime for tone/style (Requirement 8)
7. **AI has BigQuery access** - The development AI can query the actual database to build/verify golden knowledge examples, check edge cases, and validate SQL correctness during development

---
---

## Implementation Log

### 2026.02.07 - Initial implementation completed

Full LangGraph agent implemented and tested. All nodes working end-to-end:
- **Router** classifies intent (data_query vs general) via Gemini structured prompt
- **SQL Generator** produces BigQuery SQL using schema + golden knowledge few-shot examples, with self-correction on retry
- **SQL Executor** runs queries via BigQueryRunner, feeds errors back for retry loop (max 3)
- **PII Filter** drops PII columns from results using pandas, appends to collected_data
- **Report Writer** formats executive reports using persona.yaml tone/style settings
- **General Response** handles non-data questions
- **MemorySaver** checkpointer enables conversation continuity across turns
- Gemini 2.5 Flash at temperature 0.7, API key loaded from GOOGLE_API_KEY_PAID env var
- Nodes split into individual files under `src/nodes/` with shared setup in `nodes/shared.py`

**Final file structure:**

```
opsfleet langgraph/
├── .env                                 # API keys (GOOGLE_API_KEY_PAID)
├── pyproject.toml                       # UV project dependencies
├── uv.lock
├── CLAUDE.md                            # This file
├── TODO.md                              # Assignment specification
├── docs/                                # Architecture diagrams
│   ├── bq_thelook_schema.png
│   ├── full graph/                      # Full system design diagrams
│   └── current_project/                 # Current prototype graph diagram
└── src/
    ├── main.py                          # CLI entry point (input loop)
    ├── graph.py                         # LangGraph workflow (nodes, edges, conditional routing)
    ├── state.py                         # AgentState TypedDict
    ├── config.py                        # Constants, paths, load_persona(), load_db_schema()
    ├── console.py                       # Rich console helpers (print_step, print_sql, print_report)
    ├── database/
    │   ├── bq_client.py                 # BigQueryRunner class (provided)
    │   └── db_schema.md                 # Database schema reference
    ├── nodes/
    │   ├── __init__.py                  # Re-exports all node functions
    │   ├── shared.py                    # LLM instance, BQ client, schema text
    │   ├── router.py                    # Classify intent (data_query vs general)
    │   ├── golden_knowledge.py          # Load golden knowledge few-shot examples into state
    │   ├── sql_generator.py             # Generate BigQuery SQL with few-shot + self-correction
    │   ├── sql_executor.py              # Execute SQL, return markdown or error
    │   ├── pii_filter.py                # Drop PII columns, collect result into collected_data
    │   ├── report_writer.py             # Executive report with persona tone/style
    │   └── general_response.py          # Handle greetings, schema questions, capabilities
    ├── golden_knowledge/
    │   └── golden_knowledge.json        # 5 few-shot examples (Question -> SQL -> Report)
    ├── persona/
    │   └── persona.yaml                 # Editable tone/style for reports (Requirement 8)
    └── questions/
        └── test_questions.md            # 7 curated test questions with expected behavior
```
