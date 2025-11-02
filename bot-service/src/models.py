from pydantic import BaseModel


class MessageRequest(BaseModel):
    """Incoming message from Connector Service."""
    telegram_id: str
    username: str | None = None
    message: str


class MessageResponse(BaseModel):
    """Response to be sent back to user."""
    success: bool
    message: str

