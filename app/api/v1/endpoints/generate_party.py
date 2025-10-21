from fastapi import APIRouter, Request, HTTPException
import asyncio

from app.schemas.schema import PartyInput, PartyDetails, PartyData
from app.services.party.party import PartyPlanGenerator
from app.utils.helper import filter_data


router = APIRouter()

@router.post("/party_generate")
async def create_party_plan(party_input: PartyInput, request: Request):
    try:
        product = request.app.state.product_data  # ✅ fetch product
        print("product-------------------",product)
        generator = PartyPlanGenerator()
        result = generator.generate_full_party_json(party_input, product)
        
        
        return result
    except Exception as e:
        return {"error": str(e)}