from fastapi import APIRouter, Request, HTTPException
import asyncio
import time 
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from app.schemas.schema import PartyInput, PartyDetails, PartyData
from app.services.party.party import PartyPlanGenerator
from app.utils.helper import filter_data


router = APIRouter()

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



@router.post("/party_generate")
async def create_party_plan(party_input: PartyInput, request: Request):
    try:
        st = time.perf_counter()
        product = request.app.state.product_data or []  # fetch product (may be [] if not loaded)
        # print("product-------------------",product)
        generator = PartyPlanGenerator()
        result = generator.generate_full_party_json(party_input, product)
        
        ed = time.perf_counter()
        print(f"Party plan generated in {ed - st:0.4f} seconds")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))