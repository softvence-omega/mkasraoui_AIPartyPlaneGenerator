# app/api/v1/endpoints/generate_card.py
from fastapi import APIRouter, HTTPException
from app.schemas.invite import InvitationRequest, InvitationResponse, ImageInfo
from app.services import generator

router = APIRouter(prefix="/api/v1", tags=["generate"])

@router.post("/generate-card", response_model=InvitationResponse)
def generate_card(req: InvitationRequest):
    try:
        data = req.dict()
        # 1) generate text (optional)
        invitation_text = generator.generate_invitation_text(data)
        if invitation_text:
            data["custom_message"] = invitation_text

        # 2) generate image(s) and upload to Cloudinary
        images = generator.generate_birthday_card_image(data)

        images_out = [ImageInfo(url=i["url"], public_id=i.get("public_id")) for i in images]
        return InvitationResponse(invitation_text=invitation_text, images=images_out)
    except Exception as e:
        # log / raise
        raise HTTPException(status_code=500, detail=str(e))
