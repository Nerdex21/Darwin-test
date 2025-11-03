# Bot Service

Python service that processes expense messages using LangChain and OpenAI GPT-3.5-turbo.

## Description

This service is the core of the expense tracking system. It:
- Validates user authorization against a PostgreSQL whitelist
- Routes messages to appropriate handlers (expense, query, or other)
- Parses natural language expense messages using LLM
- Handles complex queries about expenses using a LangChain Agent
- Returns responses in the same language as the user input

**Architecture:**
```
Message → Router (LLM) → Expense Service / Query Agent → PostgreSQL
```

## Tech Stack

- **Python 3.11+** - Programming language
- **FastAPI** - Web framework
- **LangChain** - LLM orchestration
- **OpenAI GPT-3.5-turbo** - Language model
- **PostgreSQL** - Database
- **Uvicorn** - ASGI server

## Environment Variables

```env
# Database
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=expense_tracker
DATABASE_USER=expense_user
DATABASE_PASSWORD=expense_pass

# OpenAI
OPENAI_API_KEY=sk-proj-your_api_key_here

# LangSmith (optional, for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_api_key_here
LANGCHAIN_PROJECT=expense-tracker-bot

# Service
SERVICE_PORT=8000
```

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "healthy", "service": "bot-service"}
```

### `POST /process-message`
Process an incoming message from a Telegram user.

**Request:**
```json
{
  "telegram_id": "string",
  "username": "string",
  "message": "string"
}
```

**Responses:**
- **200 OK** - Message processed successfully
- **403 Forbidden** - User not authorized
- **422 Validation Error** - Invalid request
- **500 Internal Server Error** - Failed to save

## Expense Categories

- Housing
- Transportation
- Food
- Utilities
- Insurance
- Medical/Healthcare
- Savings
- Debt
- Education
- Entertainment
- Other

## Query Examples

- `"How much did I spend on food?"`
- `"Show me my spending breakdown"`
- `"What are my last 5 expenses?"`
- `"Show me all pizza expenses"`
- `"List all my food expenses"`

## Running Locally

**With Docker Compose:**
```bash
docker-compose up --build bot-service
```

**Standalone (development):**
```bash
cd bot-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

export OPENAI_API_KEY=your_key_here
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=expense_tracker
export DATABASE_USER=expense_user
export DATABASE_PASSWORD=expense_pass

python -m src.main
```

Service runs at `http://localhost:8000`

## Testing

**Swagger UI:**
```
http://localhost:8000/docs
```

**curl:**
```bash
# Add expense
curl -X POST http://localhost:8000/process-message \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":"123456789","username":"test","message":"Pizza 20 bucks"}'

# Query expenses
curl -X POST http://localhost:8000/process-message \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":"123456789","username":"test","message":"How much on food?"}'
```

## LangSmith Tracing

To enable LLM debugging:

1. Get API key from https://smith.langchain.com/
2. Add to `.env`:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_your_key_here
   ```
3. Restart service
4. View traces at https://smith.langchain.com/

