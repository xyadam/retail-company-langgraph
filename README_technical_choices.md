# Technical Choices

## Why Gemini 2.5 Flash

I went with Gemini 2.5 Flash as the LLM for this project. A few reasons:

- It has a very large context window (1 million tokens) which is important here because we're feeding database schemas, golden knowledge examples, and query results into the prompt all at once. With a smaller context model this would be a constant headache.
- It's fast. For a chat agent where a manager is waiting for a response, latency matters.
- It has built-in thinking/reasoning capabilities, which helps with SQL generation or complex analytics.
- Cost-wise it's very reasonable for the volume of processing we need. Each request includes schema text, few-shot examples, and sometimes large result tables, so per-token cost adds up quickly with more expensive models.
- For production deployment, Gemini is available on Google Vertex AI with EU data residency (region: europe-west1), which matters for GDPR compliance. Since we're already on GCP for BigQuery, staying in the Google ecosystem avoids cross-cloud data transfer issues.
- It handles structured output well, which we use for the router (intent classification) and could use for the SQL validator in the full system.

I considered OpenAI GPT models but since we're already deep in the GCP ecosystem with BigQuery, keeping everything Google-side simplifies auth, billing, and data residency.

## Why LangGraph

LangGraph was chosen over plain LangChain chains or a custom state machine for a few key reasons:

- **The retry loop.** The self-correction cycle (sql_executor fails → feed error back to sql_generator → try again) is a natural graph cycle. In LangGraph this is just a conditional edge pointing back to an earlier node. In a plain chain you'd have to hack around it with recursion or manual loops.
- **Conditional routing.** The router classifies intent into data_query vs general (and report_action in the full system). LangGraph's `add_conditional_edges` makes this clean — each branch is just a different path through the graph.
- **State management.** The `AgentState` TypedDict carries everything between nodes (SQL, results, retry count, error messages). Each node reads what it needs and writes what it produces. No global variables, no passing 10 arguments between functions.
- **Extensibility.** Looking at the full system requirements (QA validation, report management, delete confirmation, logging), each one is a new node with edges. Adding a feature means adding a node and wiring it in, not rewriting the pipeline. The sql_validator for example slots right between sql_generator and sql_executor with zero changes to existing nodes.
- **Built-in checkpointing.** MemorySaver gives us conversation continuity across turns for free. The manager asks "top products by revenue" and then follows up with "break that down by month" — LangGraph handles the message history persistence automatically.
- **Visualization.** `draw_mermaid_png()` renders the actual compiled graph, which is useful both for development (debugging the flow) and for the architecture diagram deliverable.

The assignment specifically recommended LangGraph/LangChain v1,. The graph-based approach maps very naturally to this kind of multi-step agent with feedback loops.

## Why BigQuery

This one was given by the assignment — the dataset lives in `bigquery-public-data.thelook_ecommerce`. But it's also a good fit:

- Read-only access to a public dataset, no infrastructure to manage
- Free tier (1TB/month) is more than enough for this use case
- The provided `BigQueryRunner` wrapper keeps the integration simple
- SQL dialect is standard enough that the LLM generates correct queries most of the time

## Other choices

- **Rich** for CLI output formatting — colored panels for SQL queries, step indicators, error messages. Makes the CLI output readable without building a UI.
- **Pandas** for result processing — the PII filter drops columns from DataFrames, and we convert results to dict/markdown for the report writer. Pandas is the natural tool for this.
- **YAML for persona config** — the CEO wants to change report tone weekly without code deployment (Req 8). A YAML file is the simplest thing that works. In production this would be in cloud storage or an admin UI, but for a prototype, editing a YAML file demonstrates the concept without over-engineering it.
- **Golden Knowledge as JSON** — the few-shot examples are stored in a simple JSON file. The prototype loads them all into the prompt. The full system design shows a `golden_examples` node that would do semantic similarity search to pick the most relevant examples, but for a prototype with 5-10 examples, loading them all works fine and avoids adding a vector database dependency.
