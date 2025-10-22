# app/schemas/contact.py
from pydantic import BaseModel
from typing import Optional

class ContactMessageCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str