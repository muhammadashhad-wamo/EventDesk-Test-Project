from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Annotated[str, Field(min_length=1, max_length=100)]
    street: Annotated[str, Field(min_length=1, max_length=50)]
    city: Annotated[str, Field(min_length=1, max_length=50)]
    country: Annotated[str, Field(min_length=1, max_length=50)]
    is_active: bool = True