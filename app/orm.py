from datetime import datetime as DateTime
from typing import Optional

from sqlmodel import SQLModel, Field


class _TableWithMetaData(SQLModel):
    createdts: Optional[DateTime]
    createdby_userid: Optional[int] = Field(foreign_key="login.userid")
    lastupdatedts: Optional[DateTime]
    lastupdatedby_userid: Optional[int] = Field(foreign_key="login.userid")
    deactivatedts: Optional[DateTime] = None
    deactivatedby_userid: Optional[int] = Field(foreign_key="login.userid")


class Parcel(_TableWithMetaData, table=True):
    parcelkey: int = Field(primary_key=True)
    parcelidcnty: str
    deactivatedts: Optional[DateTime] = None

    @property
    def url(self):
        """Allegheny County Real Estate Portal URL for the parcel."""
        # This property was originally created for debugging
        return f"https://www2.alleghenycounty.us/RealEstate/GeneralInfo.aspx?ParcelID={self.parcelidcnty}"


class ParcelMailingAddress(_TableWithMetaData, table=True):
    parcel_parcelkey: int = Field(foreign_key="parcel.parcelkey", primary_key=True)
    mailingaddress_addressid: int = Field(foreign_key="mailingAddress.addressid", primary_key=True)
    linkedobjectrole_lorid: int = Field(foreign_key="linkedobjectrole.lorid")


class MailingAddress(_TableWithMetaData, table=True):
    addressid: int = Field(primary_key=True)
    bldgno: Optional[str]
    street_streetid: int = Field(foreign_key="mailingstreet.streetid")
    attention: Optional[str]
    secondary: Optional[str]


class MailingStreet(_TableWithMetaData, table=True):
    streetid: int = Field(primary_key=True)
    name: str
    citystatezip_cszipid: int = Field(foreign_key="mailingcitystatezip.id")
    pobox: Optional[bool]


class MailingCityStateZip(_TableWithMetaData, table=True):
    id: int = Field(primary_key=True)
    zip_code: str
    state_abbr: str
    city: str


class HumanMailingAddress(_TableWithMetaData, table=True):
    humanmailing_humanid: int = Field(primary_key=True, foreign_key="human.humanid")
    humanmailing_addressid: int = Field(primary_key=True, foreign_key="mailingaddress.addressid")


class Human(_TableWithMetaData, table=True):
    humanid: int = Field(primary_key=True)
    name: str
    businessentity: bool
    multihuman: Optional[bool]
