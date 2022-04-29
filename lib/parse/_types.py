from pydantic import BaseModel, validator
from typing import Optional


class Line1(BaseModel):
    is_pobox: Optional[bool]
    attn: Optional[str]
    number: Optional[str]
    street: Optional[str]
    secondary: Optional[str] = None


class Line2(BaseModel):
    city: str
    state: str


class Line3(BaseModel):
    zip: str
