from typing import Optional, TypedDict

from sqlmodel import SQLModel

from app import orm
from lib.types import Line1, Line2, Line3


###
# Generics
###
# Generics seem to mess with SQL Model.
# Since they don't matter at all I am not going to type these classes
# O = TypeVar("O", bound="_BaseOwner")
# M = TypeVar("M", bound="_BaseMailing")
# OM = TypeVar("OM")
#
#
# class _BaseOwner(SQLModel):
#     name: str
#
#
# class _BaseMailing(SQLModel):
#     line1: Optional[Line1]
#     line2: Optional[Line2]
#     line3: Optional[Line3]
#
#
# class _BaseOwnerAndMailing(SQLModel):
#     owner: Optional[O]
#     mailing: M
#
#
# class _BaseGeneralAndMortgage(SQLModel):
#     general: OM
#     mortgage: OM


###
# Shared
###





# class CogOwner(SQLModel):
#     human: orm.Human
#
#
# class CogMailing(SQLModel):
#     parcel: orm.Parcel
#     parcel_mailing_address: orm.ParcelMailingAddress
#     mailing_address: orm.MailingAddress
#     mailing_street: orm.MailingStreet
#     city_state_zip: orm.MailingCityStateZip
#
#
# class CogOwnerAndMailing(SQLModel):
#     owner: CogOwner
#     mailing: CogMailing
#     owner_mailing: orm.HumanMailingAddress
#
#
# class CogGeneralAndMortgage(SQLModel):
#     general: CogOwnerAndMailing
#     mortgage: CogOwnerAndMailing
