from typing import Optional

from pydantic import validator
from sqlmodel import SQLModel
from app import orm
from lib.models import DeliveryAddressLine, LastLine


class Owner(SQLModel):
    name: str
    is_multi_entity: Optional[bool]


class Mailing(SQLModel):
    delivery: DeliveryAddressLine
    last: LastLine


class OwnerAndMailing(SQLModel):
    owner: Optional[Owner] = None
    mailing: Optional[Mailing] = None

class ParceladdrAndOwnerAndMailing(SQLModel):
    parceladdr: Optional[Mailing] = None
    owner: Optional[Owner] = None
    mailing: Optional[Mailing] = None


class GeneralAndMortgage(SQLModel):
    general: ParceladdrAndOwnerAndMailing
    mortgage: OwnerAndMailing


class CogTables(SQLModel):
    parcel: Optional[orm.Parcel]
    address: Optional[orm.MailingAddress]
    parcel_address: Optional[orm.ParcelMailingAddress]
    street: Optional[orm.MailingStreet]
    city_state_zip: Optional[orm.MailingCityStateZip]
    human: Optional[orm.Human]
    human_address: Optional[orm.HumanMailingAddress]
    human_parcel: Optional[orm.HumanParcel]

    # @validator("address")
    # def assert_either_all_or_none_of_address_street_and_city_state_zip(cls, v, values):
    #     if v is None:
    #         assert values["street"] is None and values["city_state_zip"] is None
    #     else:
    #         breakpoint()
    #         assert values["street"] and values["city_state_zip"]

    @property
    def has_address_tables(self) -> bool:
        # Todo: this sanity check belongs in a validator, but the initial one I wrote didn't work
        address_fields = self.address, self.street, self.city_state_zip
        assert not any(address_fields) or all(address_fields), "failed sanity check"
        return True if all([self.address, self.street, self.city_state_zip]) else False


class CogGeneralAndMortgage(SQLModel):
    general: Optional[CogTables]
    mortgage: Optional[CogTables]


class SyncedParcelSummery(SQLModel):
    pass


class MunicipalitySyncData(SQLModel):
    total: int
    skipped: list[str]
