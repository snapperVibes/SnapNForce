from typing import Optional

from sqlmodel import SQLModel
from app import orm
from lib.types import Line1, Line2, Line3


class Owner(SQLModel):
    name: str
    is_multi_entity: Optional[bool]


class Mailing(SQLModel):
    line1: Line1
    line2: Line2
    line3: Line3


class OwnerAndMailing(SQLModel):
    owner: Optional[Owner] = None
    mailing: Optional[Mailing] = None


class GeneralAndMortgage(SQLModel):
    general: OwnerAndMailing
    mortgage: OwnerAndMailing


class CogTables(SQLModel):
    parcel: Optional[orm.Parcel]
    address: Optional[orm.MailingAddress]
    parcel_address: Optional[orm.ParcelMailingAddress]
    street: Optional[orm.MailingStreet]
    city_state_zip: Optional[orm.MailingCityStateZip]
    human: Optional[orm.Human]
    human_address: Optional[orm.HumanMailingAddress]


class CogGeneralAndMortgage(SQLModel):
    general: Optional[CogTables]
    mortgage: Optional[CogTables]
