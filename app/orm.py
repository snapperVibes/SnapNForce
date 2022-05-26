from datetime import datetime as DateTime
from typing import Optional

from sqlmodel import SQLModel, Field


class _BaseModel(SQLModel):
    createdts: Optional[DateTime]
    createdby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")
    lastupdatedts: Optional[DateTime]
    lastupdatedby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")
    deactivatedts: Optional[DateTime] = None
    deactivatedby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")


class Parcel(_BaseModel, table=True):
    parcelkey: int = Field(default=None, primary_key=True)
    parcelidcnty: str
    deactivatedts: Optional[DateTime] = None
    muni_municode: int = Field(default=None, foreign_key="municipality.municode")

    @property
    def url(self):
        """Allegheny County Real Estate Portal URL for the parcel."""
        # This property was originally created for debugging
        return f"https://www2.alleghenycounty.us/RealEstate/GeneralInfo.aspx?ParcelID={self.parcelidcnty}"


class MailingAddress(_BaseModel, table=True):
    addressid: int = Field(default=None, primary_key=True)
    bldgno: Optional[str]
    street_streetid: int = Field(default=None, foreign_key="mailingstreet.streetid")
    attention: Optional[str]
    secondary: Optional[str]


class MailingStreet(_BaseModel, table=True):
    streetid: int = Field(primary_key=True)
    name: str
    citystatezip_cszipid: int = Field(default=None, foreign_key="mailingcitystatezip.id")
    pobox: Optional[bool]


class MailingCityStateZip(_BaseModel, table=True):
    id: int = Field(default=None, primary_key=True)
    zip_code: str
    state_abbr: str
    city: str


class Human(_BaseModel, table=True):
    humanid: int = Field(default=None, primary_key=True)
    name: str
    businessentity: bool
    multihuman: Optional[bool]


class Municipality(SQLModel, table=True):
    municode: int = Field(default=None, primary_key=True)
    muniname: str


###
# Link tables


class _LinkModel(_BaseModel):
    linkid: int = Field(primary_key=True)
    linkedobjectrole_lorid: int = Field(foreign_key="linkedobjectrole.lorid")


class ParcelMailingAddress(_LinkModel, table=True):
    parcel_parcelkey: int = Field(foreign_key="parcel.parcelkey")
    mailingaddress_addressid: int = Field(foreign_key="mailingAddress.addressid")


class HumanMailingAddress(_LinkModel, table=True):
    humanmailing_humanid: int = Field(foreign_key="human.humanid")
    humanmailing_addressid: int = Field(foreign_key="mailingaddress.addressid")


class HumanParcel(_LinkModel, table=True):
    human_humanid: int = Field(foreign_key="human.humanid")
    parcel_parcelkey: int = Field(foreign_key="parcel.parcelkey")

