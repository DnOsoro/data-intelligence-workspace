# Data Intelligence Workspace

An AI-powered analytics workspace for querying structured data using natural language.

## Architecture

The system combines:

- Natural language analytics
- Schema-aware table selection
- Agentic Text-to-SQL
- DuckDB execution
- SQL AST validation
- Query observability
- Streaming responses
- Interactive analytical visualizations

## Core AI Pipeline

1. User submits a natural language question.
2. Domain Architect identifies the relevant tables.
3. SQL Analyst generates SQL using the selected schema.
4. SQL Guardrails validate the generated SQL.
5. DuckDB executes the approved query.
6. Results are processed for presentation.
7. The frontend displays data, SQL, and visual analytics.

## Technology

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend

- Python
- FastAPI
- DuckDB
- SQLGlot

### AI

- Gemini
- Agent-based query orchestration

## Development

Frontend and backend are developed independently and communicate through the API layer.