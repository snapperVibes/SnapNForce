from datetime import datetime as DateTime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class _BaseModel(SQLModel):
    createdts: Optional[DateTime]
    createdby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")
    lastupdatedts: Optional[DateTime]
    lastupdatedby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")
    deactivatedts: Optional[DateTime] = None
    deactivatedby_userid: Optional[int] = Field(default=None, foreign_key="login.userid")


# Linking Tables
###


class _LinkModel(_BaseModel):
    linkid: int = Field(default=None, primary_key=True)
    linkedobjectrole_lorid: int = Field(foreign_key="linkedobjectrole.lorid")


class ParcelMailingAddress(_LinkModel, table=True):
    __tablename__ = "parcelmailingaddress"


    parcel_parcelkey: Optional[int] = Field(default=None, foreign_key="parcel.parcelkey", primary_key=True)
    mailingaddress_addressid: Optional[int] = Field(default=None, foreign_key="mailingaddress.addressid", primary_key=True)

    parcel: "Parcel" = Relationship(back_populates="mailingaddress_links")
    mailingaddress: "MailingAddress" = Relationship(back_populates="parcel_links")


class HumanMailingAddress(_LinkModel, table=True):
    humanmailing_humanid: int = Field(foreign_key="human.humanid", primary_key=True)
    humanmailing_addressid: int = Field(foreign_key="mailingaddress.addressid", primary_key=True)


class HumanParcel(_LinkModel, table=True):
    human_humanid: int = Field(foreign_key="human.humanid")
    parcel_parcelkey: int = Field(foreign_key="parcel.parcelkey")

    source_sourceid: int = Field(foreign_key="bobsource.sourceid")
    linkedobjectrole_lorid: int = Field(foreign_key="linkedobjectrole.lorid")


# Data tables
###


class Municipality(SQLModel, table=True):
    municode: int = Field(default=None, primary_key=True)
    muniname: str



class MailingAddress(_BaseModel, table=True):
    __tablename__ = "mailingaddress"

    addressid: int = Field(default=None, primary_key=True)
    bldgno: Optional[str]
    street_streetid: int = Field(default=None, foreign_key="mailingstreet.streetid")
    attention: Optional[str]
    secondary: Optional[str]

    parcel_links: List["ParcelMailingAddress"] = Relationship(back_populates="mailingaddress")
    # parcels: List["Parcel"] = Relationship(
    #     back_populates="mailing_addresses", link_model=ParcelMailingAddress
    # )
    street: "MailingStreet" = Relationship(back_populates="mailing_addresses")
    humans: List["Human"] = Relationship(back_populates="mailing_addresses", link_model=HumanMailingAddress)



class Parcel(_BaseModel, table=True):
    __tablename__ = "parcel"

    parcelkey: int = Field(default=None, primary_key=True)
    parcelidcnty: str
    muni_municode: int = Field(default=None, foreign_key="municipality.municode")

    mailingaddress_links: List[ParcelMailingAddress] = Relationship(back_populates="parcel")

    # mailing_addresses: List["MailingAddress"] = Relationship(
    #     back_populates="parcels", link_model=ParcelMailingAddress
    # )
    humans: List["Human"] = Relationship(
        back_populates="parcels", link_model=HumanParcel
    )

    @property
    def url(self):
        """Allegheny County Real Estate Portal URL for the parcel."""
        # This property was originally created for debugging
        return f"https://www2.alleghenycounty.us/RealEstate/GeneralInfo.aspx?ParcelID={self.parcelidcnty}"


class MailingStreet(_BaseModel, table=True):
    streetid: int = Field(primary_key=True)
    name: str
    citystatezip_cszipid: int = Field(default=None, foreign_key="mailingcitystatezip.id")
    pobox: Optional[bool]

    mailing_addresses: List[MailingAddress] = Relationship(back_populates="street")

    citystatezip: "MailingCityStateZip" = Relationship(back_populates="streets")


class MailingCityStateZip(_BaseModel, table=True):
    id: int = Field(default=None, primary_key=True)
    zip_code: str
    state_abbr: str
    city: str

    streets: List[MailingStreet] = Relationship(back_populates="citystatezip")


class Human(_BaseModel, table=True):
    humanid: int = Field(default=None, primary_key=True)
    name: str
    businessentity: bool
    multihuman: Optional[bool]

    mailing_addresses: List["MailingAddress"] = Relationship(back_populates="humans", link_model=HumanMailingAddress)
    parcels: List["Parcel"] = Relationship(back_populates="humans", link_model=HumanParcel)



