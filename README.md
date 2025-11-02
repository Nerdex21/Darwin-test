# Darwin Expense Tracker Bot

Telegram bot for expense tracking using LangChain and GPT-3.5 to analyze natural language messages and automatically save them to PostgreSQL.

## Description

Send messages like "Pizza 20 bucks" or "Uber to work 15.50" and the bot automatically:
- Identifies it as an expense
- Extracts description, amount, and category
- Saves it to the database
- Confirms with a response

**Architecture:**
```
Telegram → Connector Service (Node.js/TS) → Bot Service (Python/LangChain) → PostgreSQL
```

## Requirements

- Docker & Docker Compose
- OpenAI API Key
- Telegram Bot Token

## Local Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Nerdex21/Darwin-test.git
cd Darwin-test
```

**2. Create `.env` file in the root:**
```env
OPENAI_API_KEY=sk-proj-your_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**3. Start the services:**
```bash
docker-compose up --build
```

This will start:
- PostgreSQL on port `5431`
- Bot Service (API) on port `8000`
- Connector Service (Telegram Bot)

**4. Test the bot:**
- Find your bot on Telegram
- Send: `Pizza 20 bucks`
- You should receive: `Food expense added ✅`

## Test Users

The `init.sql` creates whitelisted users for testing:
- `telegram_id: "123456789"` → test_user_1
- `telegram_id: "987654321"` → test_user_2

**To add your user:** Edit `init.sql` and restart with `docker-compose down -v && docker-compose up --build`

## Tech Stack

- **Bot Service:** Python 3.11, FastAPI, LangChain, OpenAI GPT-3.5
- **Connector Service:** Node.js 20, TypeScript, ESM
- **Database:** PostgreSQL 15
- **Deployment:** Docker, Railway
