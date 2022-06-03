from sqlmodel import Session, select

from app.orm import *


def parcel(db: Session, model: Parcel) -> Optional[Parcel]:
    return db.exec(
        select(Parcel).where(
            Parcel.parcelidcnty == model.parcelidcnty,
            Parcel.deactivatedts == None
        )
    ).one_or_none()


def city_state_zip(db, model: MailingCityStateZip) -> MailingCityStateZip:
    return db.exec(
        select(MailingCityStateZip).where(
            MailingCityStateZip.zip_code == model.zip_code,
            MailingCityStateZip.state_abbr == model.state_abbr,
            MailingCityStateZip.city == model.city,
            MailingCityStateZip.deactivatedts == None
        )
    ).one_or_none()


def street(db, model: MailingStreet) -> MailingStreet:
    return db.exec(
        select(MailingStreet).where(
            MailingStreet.name == model.name,
            MailingStreet.citystatezip_cszipid == model.citystatezip_cszipid,
            MailingStreet.pobox == model.pobox,
            MailingStreet.deactivatedts == None,
        )
    ).one_or_none()


def address(db, model: MailingAddress) -> MailingAddress:
    return db.exec(
        select(MailingAddress).where(
            MailingAddress.bldgno == model.bldgno,
            MailingAddress.street_streetid == model.street_streetid,
            MailingAddress.attention == model.attention,
            MailingAddress.secondary == model.secondary,
            MailingAddress.deactivatedts == None
        )
    ).one_or_none()


def human(db, model: Human) -> Human:
    return db.exec(
        select(Human).where(
            Human.name == model.name,
            Human.businessentity == model.businessentity,
            Human.multihuman == model.multihuman,
            Human.deactivatedts == None
        )
    ).one_or_none()


def linked_parcel_and_address(db, model: ParcelMailingAddress) -> ParcelMailingAddress:
    return db.exec(
        select(ParcelMailingAddress).where(
            ParcelMailingAddress.parcel_parcelkey == model.parcel_parcelkey,
            ParcelMailingAddress.mailingaddress_addressid == model.mailingaddress_addressid,
            HumanMailingAddress.linkedobjectrole_lorid == model.linkedobjectrole_lorid,
            ParcelMailingAddress.deactivatedts == None
        )
    ).one_or_none()


def linked_human_and_address(db, model: HumanMailingAddress) -> HumanMailingAddress:
    return db.exec(
        select(HumanMailingAddress).where(
            HumanMailingAddress.humanmailing_humanid == model.humanmailing_humanid,
            HumanMailingAddress.humanmailing_addressid == model.humanmailing_addressid,
            HumanMailingAddress.linkedobjectrole_lorid == model.linkedobjectrole_lorid,
            HumanMailingAddress.deactivatedts == None
        )
    ).one_or_none()


def linked_human_and_parcel(db, model: HumanParcel) -> HumanParcel:
    return db.exec(
        select(HumanParcel).where(
            HumanParcel.human_humanid == model.human_humanid,
            HumanParcel.parcel_parcelkey == model.parcel_parcelkey,
            HumanParcel.linkedobjectrole_lorid == model.linkedobjectrole_lorid,
            HumanParcel.deactivatedts == None
        )
    )