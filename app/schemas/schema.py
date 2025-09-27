from pydantic import BaseModel, Field
from typing import Optional



class Shirt(BaseModel):
    t_shirt_type : str = "Type of shirt"
    t_shirt_size : str = "Size of shirt"
    gender : str = "Gender of shirt"
    t_shirt_color : str = "Color of shirt"
    age : int = 7
    t_shirt_theme : str = "Theme of shirt"
    optional_description : Optional[str] = None


