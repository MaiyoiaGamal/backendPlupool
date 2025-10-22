# app/api/v1/endpoints/contact.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.contact import ContactMessageCreate
from app.models.contact_message import ContactMessage

router = APIRouter()

@router.post("")
def send_contact_message(
    data: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    db_msg = ContactMessage(**data.model_dump())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return {"detail": "تم إرسال رسالتك بنجاح!"}