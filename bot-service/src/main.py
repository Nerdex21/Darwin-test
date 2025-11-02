from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.models import MessageRequest, MessageResponse
from src.database import db
from src.expense_parser import expense_parser
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
    
    This endpoint:
    1. Verifies the user is whitelisted
    2. Parses the message to extract expense information
    3. Stores the expense in the database
    4. Returns an appropriate response
    """
    # Check if user is whitelisted and get user ID
    user_id = db.get_user_id(request.telegram_id)
    if not user_id:
        # User not whitelisted - 403 Forbidden
        raise HTTPException(
            status_code=403,
            detail="User not authorized"
        )
    
    # Parse the message to check if it's an expense
    expense_info = expense_parser.parse_message(request.message)
    
    if not expense_info:
        # Not an expense message - 200 OK with success=false
        # (message was processed successfully, just not an expense)
        return MessageResponse(
            success=False,
            message="Not an expense message"
        )
    
    # Add expense to database
    success = db.add_expense(
        user_id=user_id,
        description=expense_info.description,
        amount=expense_info.amount,
        category=expense_info.category
    )
    
    if success:
        return MessageResponse(
            success=True,
            message=f"{expense_info.category} expense added ✅"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to save expense"
        )


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )

