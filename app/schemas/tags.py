from pydantic import BaseModel


class TagModel(BaseModel):
    text: str


class TagDB(TagModel):
    id: int

    class Config:
        from_attributes = True
