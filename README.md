# Blinkit Quick Commerce Intelligence — SQL Analyst Agent

This project is the first agent in a planned multi-agent quick-commerce intelligence system. The current release focuses on a natural-language SQL analyst for exploring Blinkit-style operational data stored in PostgreSQL.

## What the agent does

Ask a business question in plain English. The LangGraph workflow:

1. Curates the question for analysis.
2. Reads table names, column types, and up to five sample records from the PostgreSQL `public` schema.
3. Uses Groq's `openai/gpt-oss-120b` model to generate PostgreSQL SQL. The prompt asks for at most 10 rows unless a different limit is requested.
4. Uses the model as a structured-output judge to decide whether the SQL appears read-only.
5. Executes a query the judge approves and summarizes its result in plain language. If the judge rejects it, the workflow returns the judge's reason without running the query.

The judge is an LLM-based check; it is not a database security boundary. Use a PostgreSQL account restricted to read-only access when running the app.

## Data model

The included CSV data represents five related tables:

| Table | Example information |
| --- | --- |
| `customers` | Customer profile, area, segment, order count, average order value |
| `products` | Product, category, brand, price, margin, shelf-life and stock thresholds |
| `orders` | Order time, delivery status, payment method, total and store |
| `order_items` | Products and quantities in each order |
| `inventory` | Daily stock received and damaged stock by product |

The graph is implemented in [`agents/sql_agent.py`](agents/sql_agent.py), with PostgreSQL access in [`utils/database.py`](utils/database.py) and model selection in [`utils/llm_pick.py`](utils/llm_pick.py).

## Setup

Requirements: Python 3.11+, PostgreSQL, and a Groq API key.

1. Install dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

2. Create a PostgreSQL database and a dedicated user. Grant that user read-only access to the data schema.
3. Copy `.env.example` to `.env` and fill in the Groq key and PostgreSQL connection values:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   host=localhost
   port=5432
   user=your_read_only_user
   password=your_password
   database=your_database_name
   ```

4. Load the sample CSVs into the database:

   ```bash
   uv run python data_feed.py
   ```

   **Warning:** `data_feed.py` truncates the five target tables before loading the CSVs. Run it only against a database where replacing those tables' data is intended.

5. Start the chat UI:

   ```bash
   uv run streamlit run app.py
   ```

Alternatively, run the graph directly with `uv run python agents/sql_agent.py`.

## Example questions

- Which payment methods are most common?
- What are the top 10 products by quantity sold?
- Which delivery statuses occur most often?
- Which products have the highest damaged stock?
- Compare average order value across customer segments.

The app displays the generated SQL in an expandable panel for transparency. Do not expose a deployment with access to private or production data without appropriate authentication, network restrictions, and database permissions.

## LinkedIn post draft

I’m excited to share the first agent in my Blinkit Quick-Commerce Intelligence project: a SQL Analyst Agent that turns natural-language business questions into answers from PostgreSQL data.

The agent uses LangGraph to structure the workflow: it prepares the question, inspects the database schema, generates SQL with Groq, checks the query with a structured LLM safety judge, executes approved queries, and explains the results in plain language. I also built a Streamlit chat UI so people can ask questions and inspect the generated SQL.

The project currently works with customer, product, order, order-item, and inventory data. Example questions include identifying popular payment methods, top-selling products, delivery patterns, and inventory damage.

This is the first agent in a planned multi-agent quick-commerce analytics project. I plan to add more agents in the future to cover additional analytics workflows.

Built with Python, LangGraph, LangChain, Groq, PostgreSQL, and Streamlit.

#AI #Agents #LangGraph #PostgreSQL #Streamlit #QuickCommerce #DataAnalytics #Blinkit

