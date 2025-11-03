# Connector Service

Node.js/TypeScript service that connects Telegram Bot API with the Bot Service.

## Description

This service acts as a bridge between Telegram and the Bot Service. It:
- Listens for incoming Telegram messages via polling
- Forwards messages to the Bot Service for processing
- Returns responses to users via Telegram
- Handles unauthorized users silently (no response)
- Provides user-friendly error messages

**Architecture:**
```
Telegram API ↔ Connector Service (Node.js/TS) ↔ Bot Service (Python)
```

## Tech Stack

- **Node.js 20 LTS** - Runtime
- **TypeScript** - Type-safe JavaScript
- **ESM** - Modern module system
- **node-telegram-bot-api** - Telegram Bot SDK
- **Axios** - HTTP client

## Environment Variables

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Bot Service URL
BOT_SERVICE_URL=http://bot-service:8000
```

**Getting a Telegram Bot Token:**
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the API token provided
5. Add it to your `.env` file

## Running Locally

**With Docker Compose:**
```bash
docker-compose up --build connector-service
```

**Standalone (development):**
```bash
cd connector-service
npm install

export TELEGRAM_BOT_TOKEN=your_token_here
export BOT_SERVICE_URL=http://localhost:8000

npm run dev  # Development mode
# or
npm run build && npm start  # Production mode
```

## Scripts

```bash
npm install         # Install dependencies
npm run build       # Build TypeScript
npm start           # Start bot (production)
npm run dev         # Development with auto-reload
```

## Message Flow

1. **User sends:** `"Pizza 20 bucks"`
2. **Connector receives** and forwards to Bot Service
3. **Bot Service processes** and returns response
4. **Connector sends back:** `"Food expense added ✅"`

## Logging

All logs include prefixes for filtering:

- `[STARTUP]` - Service initialization
- `[CONFIG]` - Configuration loaded
- `[MESSAGE]` - Incoming messages
- `[SUCCESS]` - Successful operations
- `[UNAUTHORIZED]` - Unauthorized users
- `[NOT_EXPENSE]` - Non-expense messages
- `[ERROR]` - Errors
- `[TELEGRAM_BOT]` - Bot events

## Error Handling

- **Unauthorized users:** Silently ignored
- **Invalid messages:** Help message sent
- **Bot Service down:** Error logged, no user message
- **Telegram API errors:** Logged, service continues

