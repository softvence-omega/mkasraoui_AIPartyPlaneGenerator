# app/api/v1/endpoints/generate_card.py
from fastapi import APIRouter, HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from app.schemas.invite import InvitationRequest, InvitationResponse, ImageInfo
from app.services import generator

router = APIRouter(prefix="/api/v1", tags=["generate"])

def _should_retry(exception):
    # Retry for server errors and other exceptions, but not for client (4xx) HTTPExceptions
    from fastapi import HTTPException as FastAPIHTTPException
    if isinstance(exception, FastAPIHTTPException):
        return exception.status_code >= 500
    return True

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(_should_retry),
    reraise=True,
)
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
