from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.models import MessageRequest, MessageResponse
from src.services.expense_service import expense_service
from src.config import get_settings

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


@app.post("/process-message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process an incoming message from a Telegram user.
    
    This endpoint delegates all business logic to the ExpenseService.
    """
    # Delegate to service layer
    success, message, status_code = expense_service.process_message(
        telegram_id=request.telegram_id,
        message=request.message
    )
    
    # Handle HTTP errors
    if status_code:
        raise HTTPException(status_code=status_code, detail=message)
    
    # Return response
    return MessageResponse(success=success, message=message)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )

