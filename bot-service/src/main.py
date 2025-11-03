import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.config import get_settings

# Configure LangSmith BEFORE importing any LLM modules
settings = get_settings()
if settings.langchain_tracing_v2 == "true" and settings.langchain_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    print(f"[LANGSMITH] Tracing enabled for project: {settings.langchain_project}")

# Now import modules that use LLMs (they will pick up the env vars)
from src.models import MessageRequest, MessageResponse
from src.message_router import message_router
from src.services.expense_service import expense_service
from src.services.query_service import query_service

app = FastAPI(title="Expense Tracker Bot Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bot-service"}


@app.post(
    "/process-message", 
    response_model=MessageResponse,
    responses={
        200: {
            "description": "Message processed successfully",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "Food expense added ✅"}
                }
            }
        },
        403: {
            "description": "User not authorized (not in whitelist)",
            "content": {
                "application/json": {
                    "example": {"detail": "User not authorized"}
                }
            }
        },
        500: {
            "description": "Internal server error (failed to save expense)",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to save expense"}
                }
            }
        }
    }
)
async def process_message(request: MessageRequest):
    """
    Process an incoming message from a Telegram user.
    
    This endpoint:
    1. Checks user authorization
    2. Routes the message to the appropriate handler (expense or query)
    3. Delegates processing to the corresponding service
    4. Returns the response
    """
    # 1. Check if user is whitelisted FIRST (before any processing)
    from src.database import db
    user_id = db.get_user_id(request.telegram_id)
    if not user_id:
        # User not whitelisted - return 403 Forbidden
        raise HTTPException(status_code=403, detail="User not authorized")
    
    # 2. Classify the message type
    message_type = message_router.classify(request.message)
    
    # 3. Route to appropriate service
    if message_type == "expense":
        # Handle expense reporting
        success, message, status_code = expense_service.process_message(
            telegram_id=request.telegram_id,
            message=request.message
        )
    
    elif message_type == "query":
        # Handle expense queries
        success, message, status_code = query_service.process_query(
            telegram_id=request.telegram_id,
            message=request.message
        )
    
    else:
        # Handle other messages (greetings, etc.)
        return MessageResponse(
            success=False,
            message="I can help you track expenses and answer questions about your spending. Try: 'Pizza 20 bucks' or 'How much did I spend on food?'"
        )
    
    # 4. Handle HTTP errors
    if status_code:
        raise HTTPException(status_code=status_code, detail=message)
    
    # 5. Return response
    return MessageResponse(success=success, message=message)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )

