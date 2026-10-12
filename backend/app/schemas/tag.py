from typing import Annotated

from pydantic import BaseModel, ConfigDict

class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tag: str