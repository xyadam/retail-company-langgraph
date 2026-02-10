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