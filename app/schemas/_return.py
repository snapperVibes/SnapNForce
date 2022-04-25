""" Schemas that may be returned by API endpoints """
from typing import Optional

from sqlmodel import SQLModel

from lib.types import Line1, Line2, Line3


class Owner(SQLModel):
    name: str
    is_multi_entity: Optional[bool]


class Mailing(SQLModel):
    line1: Optional[Line1]
    line2: Optional[Line2]
    line3: Optional[Line3]


class OwnerAndMailing(SQLModel):
    owner: Owner
    mailing: Mailing


class GeneralAndMortgage(SQLModel):
    general: OwnerAndMailing
    mortgage: OwnerAndMailing