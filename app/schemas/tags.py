from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class TagDB(BaseModel):
    text: str
