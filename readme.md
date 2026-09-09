# Conversational SQL Agent

A read-only conversational SQL agent that turns natural-language questions into SQLite queries and returns concise answers, query results, and optional chart data.

The project uses FastAPI for the HTTP API, LangGraph to orchestrate the agent workflow, an LLM to generate and summarize results, and MCP (Model Context Protocol) to inspect and query the SQLite database.

## Features

- Natural-language questions over SQLite data
- Automatic schema discovery and caching
- SQL generation and validation through a LangGraph workflow
- Read-only query execution with `SELECT` enforcement
- Configurable retry handling for invalid SQL
- Results capped by `MAX_ROWS`
- Optional bar-chart data for suitable result sets
- Simple health-check endpoint

## Architecture

The request flows through these stages:

1. Check the user intent and reject write or destructive requests.
2. Discover and cache the database schema through MCP.
3. Generate a SQLite `SELECT` query with the configured LLM.
4. Validate the query and add a row limit when needed.
5. Execute the query through the MCP server.
6. Retry failed queries up to `MAX_RETRIES`.
7. Summarize successful results and produce optional chart data.

The MCP server is started automatically as a subprocess for each database operation. It communicates over stdio and reads the database configured by `DB_PATH`.

## Requirements

- Python 3.10 or newer
- An API key for the configured LLM provider
- Windows PowerShell, macOS/Linux shell, or an equivalent terminal

## Installation

Clone the repository and open its directory:

```bash
git clone <your-repository-url>
cd "Sql agent"
```

Create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file to `.env`:

### Windows PowerShell

```powershell
Copy-Item .example.env .env
```

### macOS/Linux

```bash
cp .example.env .env
```

Update `.env` with your LLM credentials and runtime settings:

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=your_api_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_REASONING_EFFORT=medium

DB_PATH=./sample_data/ecommerce.db
MAX_RETRIES=3
MAX_ROWS=100
```

Do not commit `.env` or API keys to GitHub. The `.gitignore` file is configured to exclude local environment files.

> The current implementation uses `ChatGroq` when `MODEL_PROVIDER` is set. The other provider packages in `requirements.txt` are available for future provider support.

## Seed the sample database

The included seed script recreates the sample ecommerce database each time it runs:

```bash
python sample_data/seed_db.py
```

This creates `sample_data/ecommerce.db` with these tables:

- `customers`
- `products`
- `orders`
- `order_items`

Run the seed script again whenever you want to reset the sample data.

## Run the API

Start the development server from the project root:

```bash
uvicorn main:app --reload
```

The API will be available at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## API usage

### Health check

```http
GET /health
```

Example response:

```json
{
  "STATUS": "ALL IS WELL"
}
```

### Ask a question

```http
POST /chat
Content-Type: application/json
```

Request body:

```json
{
  "message": "Which customers are from Chennai?"
}
```

PowerShell example:

```powershell
$body = @{ message = "Which customers are from Chennai?" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body $body
```

A session ID may be supplied by the caller and is returned in the response:

```json
{
  "message": "How many orders were placed in March 2024?",
  "session_id": "optional-client-session-id"
}
```

Example response shape:

```json
{
  "session_id": "generated-or-client-session-id",
  "answer": "There were 5 orders placed in March 2024.",
  "sql": "SELECT COUNT(*) AS order_count FROM orders WHERE order_date >= '2024-03-01' AND order_date < '2024-04-01';",
  "rows": [
    { "order_count": 5 }
  ],
  "chart_data": null
}
```

## Project structure

```text
.
├── main.py                    # FastAPI application and API routes
├── requirements.txt           # Python dependencies
├── .example.env               # Environment variable template
├── agent/
│   ├── graph.py               # LangGraph workflow definition
│   ├── llm.py                 # LLM configuration
│   ├── mcp_client.py          # MCP client helpers
│   ├── mcp_server.py          # Read-only SQLite MCP tools
│   ├── state.py               # Shared workflow state
│   └── nodes/                 # Individual workflow nodes
└── sample_data/
    └── seed_db.py             # Sample SQLite schema and data
```

## Safety and limitations

- The agent is intentionally read-only. `INSERT`, `UPDATE`, `DELETE`, schema changes, and other destructive SQL operations are rejected.
- Query results are limited to `MAX_ROWS` rows.
- The LLM must generate SQL using the discovered schema; it should not invent tables or columns.
- The schema is cached in memory, so restart the API after changing the database schema.
- `session_id` is currently returned by the API but is not used to persist conversational history between requests.

## License

Add the license that applies to your project before publishing it to GitHub.
