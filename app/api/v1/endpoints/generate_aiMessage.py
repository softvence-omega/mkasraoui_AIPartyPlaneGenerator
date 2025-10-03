# app/api/v1/endpoints/generate_card.py
from fastapi import APIRouter, HTTPException
from app.schemas.invite import InvitationMessageRequest
from app.services import generator

router = APIRouter(prefix="/api/v1", tags=["generate"])

@router.post("/generate-message")
def generate_aiMessage(req: InvitationMessageRequest):
    try:
        data = req.dict()
        # 1) generate text (optional)
        invitation_text = generator.generate_invitation_text(data)
       
        return {"invitation_Message": invitation_text}

    except Exception as e:
        # log / raise
        raise HTTPException(status_code=500, detail=str(e))
