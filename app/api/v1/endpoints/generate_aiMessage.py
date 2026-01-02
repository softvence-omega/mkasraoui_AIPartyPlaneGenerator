# app/api/v1/endpoints/generate_card.py
from fastapi import APIRouter, HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from app.schemas.invite import InvitationMessageRequest
from app.services import generator

router = APIRouter(prefix="/api/v1", tags=["generate"])

def _should_retry(exception):
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
@router.post("/generate-message")
def generate_aiMessage(req: InvitationMessageRequest):
    try:
        data = req.dict()
        # 1) generate text (optional)
        invitation_text = generator.generate_invitation_text(data)
       
        return {"invitation_Message": invitation_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
