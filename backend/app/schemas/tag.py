from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints

TagName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_lower=True, min_length=1, max_length=50),
]

class TagCreate(BaseModel):
    tag: TagName

class TagUpdate(BaseModel):
    tag: TagName

class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tag: str