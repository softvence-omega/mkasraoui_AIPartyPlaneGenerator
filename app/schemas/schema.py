from pydantic import BaseModel, Field
from typing import Optional, List

class Shirt(BaseModel):
    t_shirt_type : str = "Type of shirt"
    t_shirt_size : str = "Size of shirt"
    gender : str = "Gender of shirt"
    t_shirt_color : str = "Color of shirt"
    age : int = 7
    t_shirt_theme : str = "Theme of shirt"
    optional_description : Optional[str] = None

class PartyDetails(BaseModel):
    theme: str
    favorite_activities: List[str]

class PartyInput(BaseModel):
    person_name: str = Field(..., example="Prinom")
    person_age: int = Field(..., example=7)
    budget: float = Field(..., example=500)
    num_guests: int = Field(..., example=20)
    party_date: str = Field(..., example="2024-12-15")
    location: str = Field(..., example="New York City")
    party_details: PartyDetails


class PartyData(PartyInput):
    num_product : Optional[int]

