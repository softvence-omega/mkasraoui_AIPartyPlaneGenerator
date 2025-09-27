# app/schemas/invite.py
from pydantic import BaseModel, Field
from typing import Optional

class InvitationRequest(BaseModel):
    theme: Optional[str] = Field(None, example="Football lover")
    description: Optional[str] = Field(None, example="Playing a boy football with cake.")
    age: Optional[int] = Field(None, example=10)
    gender: Optional[str] = Field(None, example="Male")
    birthday_person_name: str = Field(..., example="Prinom")
    venue: Optional[str] = Field(None, example="Party Hall")
    date: Optional[str] = Field(None, example="12 Oct 2025")
    time: Optional[str] = Field(None, example="4:00 PM")
    contact_info: Optional[str] = Field(None, example="01610982021")

class ImageInfo(BaseModel):
    url: str
    public_id: Optional[str] = None

class InvitationResponse(BaseModel):
    invitation_text: Optional[str]
    images: list[ImageInfo] = []
