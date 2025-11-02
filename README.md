# Darwin Expense Tracker Bot

Bot de Telegram para rastreo de gastos que usa LangChain y GPT-3.5 para analizar mensajes en lenguaje natural y guardarlos automáticamente en PostgreSQL.

## Descripción

Enviá mensajes como "Pizza 20 bucks" o "Uber to work 15.50" y el bot automáticamente:
- Identifica que es un gasto
- Extrae descripción, monto y categoría
- Lo guarda en la base de datos
- Te responde confirmando

**Arquitectura:**
```
Telegram → Connector Service (Node.js/TS) → Bot Service (Python/LangChain) → PostgreSQL
```

## Requisitos

- Docker & Docker Compose
- OpenAI API Key
- Telegram Bot Token

## Setup Local

**1. Cloná el repositorio:**
```bash
git clone https://github.com/Nerdex21/Darwin-test.git
cd Darwin-test
```

**2. Creá el archivo `.env` en la raíz:**
```env
OPENAI_API_KEY=sk-proj-tu_api_key_aqui
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
```

**3. Levantá los servicios:**
```bash
docker-compose up --build
```

Esto levanta:
- PostgreSQL en puerto `5431`
- Bot Service (API) en puerto `8000`
- Connector Service (Telegram Bot)

**4. Probá el bot:**
- Buscá tu bot en Telegram
- Enviá: `Pizza 20 bucks`
- Deberías recibir: `Food expense added ✅`

## Usuarios de Prueba

El `init.sql` crea usuarios whitelisted para testing:
- `telegram_id: "123456789"` → test_user_1
- `telegram_id: "987654321"` → test_user_2

**Para agregar tu usuario:** Editá `init.sql` y reiniciá con `docker-compose down -v && docker-compose up --build`

## Tecnologías

- **Bot Service:** Python 3.11, FastAPI, LangChain, OpenAI GPT-3.5
- **Connector Service:** Node.js 20, TypeScript, ESM
- **Database:** PostgreSQL 15
- **Deployment:** Docker, Railway
