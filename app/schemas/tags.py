from pydantic import BaseModel


class TagDB(BaseModel):
    text: str
