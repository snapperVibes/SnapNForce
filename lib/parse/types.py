__all__ = ["Line1", "Line2", "Line3"]
from typing import NamedTuple, Optional


class Line1(NamedTuple):
    is_pobox: Optional[bool]
    attn: Optional[str]
    number: Optional[str]
    street: Optional[str]


class Line2(NamedTuple):
    city: str
    state: str


class Line3(NamedTuple):
    zip: str
