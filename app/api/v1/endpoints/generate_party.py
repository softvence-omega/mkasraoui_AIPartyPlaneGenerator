from fastapi import APIRouter, Request
import asyncio

from app.schemas.schema import PartyInput, PartyDetails, PartyData
from app.services.party.party import PartyPlanGenerator
from app.utils.helper import filter_data


router = APIRouter()

@router.post("/party_generate")
async def party_generate(party_input : PartyData, request : Request):

    party_data = PartyInput(
        person_name=party_input.person_name,
        person_age=party_input.person_age,
        budget=party_input.budget,
        num_guests=party_input.num_guests,
        party_date=party_input.party_date,
        location=party_input.location,
        party_details=PartyDetails(
            theme=party_input.party_details.theme,
            favorite_activities=party_input.party_details.favorite_activities
        )
    )

    party_plan = PartyPlanGenerator()
    
    try:
        # Fetch the data
        print("Fetching Data.....")
        product = request.app.state.product_data
        filtered_data = filter_data(product["data"], party_data.budget)

        ## Generate party plan
        print("Generating Party Plan.....")
        party_generated_response, gift_list = party_plan.generate_party_plan(party_data)
        await asyncio.sleep(1)

        ## Suggest Gifts
        print("Suggesting Gifts.....")
        gift_response = party_plan.suggested_gifts(
            product=filtered_data,
            suggest_gifts=gift_list,
            how_many=party_input.num_product
        )
        
    except Exception as e:
        print("Error:", e)
        return {"error": "An error occurred while processing your request."}
    
    
    return {"party_plan": party_generated_response, "suggest_gifts": gift_response, "all_product": product["data"]}


