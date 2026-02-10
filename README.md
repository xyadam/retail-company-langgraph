# OpsFleet Data Analysis Chat Agent

A LangGraph-based chat agent for retail executives. Ask natural language questions about sales, orders, and products - the agent generates SQL, queries BigQuery, and gives you a report.

## Prerequisites

- Python 3.12+
- A Gemini API key (free from [Google AI Studio](https://aistudio.google.com/apikey))
- Google Cloud authentication for BigQuery access

The dataset is public (`bigquery-public-data.thelook_ecommerce`), so no GCP billing is needed - Google gives 1TB/month free tier for BigQuery reads.

## Installation

You can install dependencies with either UV or pip, whichever you prefer:

**With UV:**
```bash
uv sync
```

**With pip:**
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with your Gemini API key:
```
GOOGLE_API_KEY_PAID=your-gemini-api-key-here
```

2. Make sure you're authenticated with Google Cloud (needed for BigQuery):
```bash
gcloud auth application-default login
```

If you don't have the gcloud CLI, follow the [BigQuery client setup guide](https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python).

## Running

**With UV:**
```bash
uv run python src/main.py
```

**With pip (after installing dependencies):**
```bash
python src/main.py
```

This starts a CLI chat loop. Type your question and press Enter. Type `exit` or `quit` to stop.

## Example questions

```
> What are the top 5 products by revenue?
> How many orders were placed last month by country?
> Which customers spent the most?          (names/emails are filtered out automatically)
> What is the average order value by country?
> break that down by month                 (follow-up works via conversation memory)
```

## What it does

The agent classifies your question as either a data query or a general question. For data queries, it generates BigQuery SQL, runs it, filters out any PII columns, and writes an executive report. For general questions (like "what tables are available?"), it responds directly.

**Implemented features:**
- **PII Masking** - customer names, emails, and addresses are blocked at the SQL level and filtered from results. The report writer is also instructed to never include personal data.
- **Self-Correction** - if the generated SQL fails (syntax error, wrong column, empty results), the agent retries up to 3 times, feeding the error message back so the LLM can fix it.
- **Golden Knowledge** - few-shot examples from `src/golden_knowledge/golden_knowledge.json` guide the SQL generation so the agent follows patterns from human analysts.
- **Persona Management** - edit `src/persona/persona.yaml` to change the report tone and style. No code changes needed, just edit the YAML.
- **Conversation Memory** - follow-up questions work because the agent keeps conversation history via LangGraph's MemorySaver.

## Project structure

```
src/
├── main.py              # CLI entry point (start here)
├── graph.py             # LangGraph workflow (nodes, edges, routing)
├── state.py             # AgentState TypedDict
├── config.py            # Constants, LLM init, file loaders
├── console.py           # Rich console output helpers
├── database/
│   ├── bq_client.py     # BigQueryRunner class
│   └── db_schema.md     # Database schema reference
├── nodes/
│   ├── router.py        # Classifies intent (data query vs general)
│   ├── sql_generator.py # Generates BigQuery SQL with few-shot examples
│   ├── sql_executor.py  # Runs SQL, validates PII, handles errors
│   ├── report_writer.py # Writes executive report with persona config
│   └── general_response.py
├── golden_knowledge/
│   └── golden_knowledge.json  # Few-shot examples (Question -> SQL)
├── persona/
│   └── persona.yaml     # Editable report tone/style
└── questions/
    └── test_questions.md # Test questions with expected behavior
```

## Documentation

- `docs/README_technical_choices.md` - why Gemini, LangGraph, BigQuery, and other tech decisions
- `docs/README_retry_explanation.md` - how the self-correction retry loop works
- `docs/full graph/full_system_mermaid.md` - full system architecture diagram (Mermaid) covering all 8 requirements
- `docs/current_project/langgraph_flow.png` - current prototype graph
- `docs/full graph/full_system_langgraph.png` - full system HLD graph
