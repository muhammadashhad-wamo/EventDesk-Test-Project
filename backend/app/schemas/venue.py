from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

class VenueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=50)

class VenueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    street: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    country: str | None = Field(default=None, min_length=1, max_length=50)

class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Annotated[str, Field(min_length=1, max_length=100)]
    street: Annotated[str, Field(min_length=1, max_length=50)]
    city: Annotated[str, Field(min_length=1, max_length=50)]
    country: Annotated[str, Field(min_length=1, max_length=50)]
    is_active: bool = True