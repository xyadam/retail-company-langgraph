# Resilience & Self-Correction (Retry Loop)

This is one of the two requirements I chose to implement in the prototype (the other being PII masking).

## The problem

LLM-generated SQL is not always correct on the first attempt. Common failure modes:

- Syntax errors (wrong BigQuery dialect, missing backticks on table names)
- Wrong column names (the LLM hallucinates a column that doesn't exist)
- Empty results (the query is valid but the filters are too narrow)
- Type mismatches (comparing a string to an int, wrong date format)

If we just show the user "something went wrong" on the first failure, the experience is terrible. Most of these are fixable if the LLM gets to see its own error and try again.

## How it works

The retry loop is a cycle in the LangGraph between `sql_executor` and `sql_generator`:

`sql_generator` ---> `sql_executor` ---> success? ---> yes ---> `report_writer`
                          \                              \
                           \--- error + retries < 3 -------> back to `sql_generator` (with error context)
                            \--- error + retries >= 3 ----> `report_writer` (apologize)

When `sql_executor` catches an error (exception from BigQuery, or 0 rows returned), it:
1. Stores the error message in state (`error_message`)
2. Increments `retry_count`
3. Returns to `sql_generator`

The `sql_generator` then sees the previous SQL and the error message in its prompt, so it can fix the specific issue. This is much more effective than just retrying blindly — the LLM knows *what* went wrong.

## Max 3 retries

The cap is 3 attempts total. This is a balance between:
- Giving the LLM enough chances to fix syntax issues (usually 1 retry is enough)
- Not burning API credits on a question that fundamentally can't be answered from the data
- Not making the user wait forever

After 3 failed attempts, the report_writer gets the error state and generates a message like "I couldn't retrieve this data — try rephrasing your question" along with what went wrong. The user isn't left staring at a crash.

## What gets retried vs what doesn't

The `sql_executor` also does SQL validation *before* running the query:
- Blocks `SELECT *` (we need explicit columns for PII filtering)
- Blocks queries that reference PII columns directly

These validation failures also count as retries and feed back to the generator with the specific reason. So if the LLM accidentally tries to select `email`, it gets told "PII column 'email' is not allowed" and regenerates without it.

## Why this matters

In practice during development, I saw the retry loop fix issues probably 60-70% of the time on the first retry. The most common pattern was the LLM using wrong backtick syntax for BigQuery table references, which it corrected immediately once it saw the error. Without the retry loop, those would have been failed responses to the user.

The key insight is that feeding the error message back to the LLM is cheap (one more API call) and very effective compared to just failing. The 3-attempt cap keeps costs bounded.
