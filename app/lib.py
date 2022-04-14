""" Common functions made from the primitives found in lib"""
import re
from typing import Callable, AnyStr, TypedDict, NamedTuple, Optional

import httpx
from bs4 import Tag, NavigableString

from lib import parse, scrape
from lib.parse.types import Line1, Line2, Line3


def get_parcel_data(parcel_id: str):
    general_data = get_general_data(parcel_id)
    tax_data = get_tax_data(parcel_id)
    return {"general": general_data, "mortgage": tax_data}


# def get_general_data(parcel_id: str):
#     return _get_data(
#         scraper=scrape.general_info,
#         parser=parse.general_content,
#         mailing_serilizer=MailingData.from_raw_general,
#         parcel_id=parcel_id
#     )

def get_tax_data(parcel_id: str):
    response = scrape.tax_info(parcel_id)
    response.raise_for_status()
    _owner, _mailing = parse.tax_content(response.content)
    owner_data = OwnerData.from_raw(_owner)
    mailing_data = MailingData.from_raw_tax(_mailing)
    return MailingAddress(owner_data, mailing_data)

# This is HOW you should structure your get_data calls
#  In practice, debugging was easier without the functional approach exampled here
# def get_tax_data(parcel_id: str):
#     return _get_data(
#         scraper=scrape.tax_info,
#         parser=parse.general_content,
#         owner_serilzer=OwnerData.from_raw,
#         mailing_serilizer=MailingData.from_raw_tax,
#         parcel_id=parcel_id
#     )
def __get_data(
    scraper: Callable[[str], httpx.Response],
    parser: Callable[
        [AnyStr], tuple[list[Tag | NavigableString], list[Tag | NavigableString]]
    ],
    owner_serilizer,
    mailing_serilizer,
    parcel_id: str,
) -> "MailingAddress":
    response = scraper(parcel_id)
    response.raise_for_status()
    _owner, _mailing = parser(response.content)
    owner_data = owner_serilizer(_owner)
    mailing_data = mailing_serilizer(_mailing)
    return MailingAddress(owner_data, mailing_data)


class OwnerData(NamedTuple):
    name: str
    is_multi_entity: bool

    @classmethod
    def from_raw(cls, data: list[Tag | NavigableString]):
        is_multi_entity = False
        owner_list = _clean_tags(data)
        # Owner names often have trailing whitespace
        #  If it isn't stripped away, the dirty_owner != clean_owner check
        #  will always return True.
        dirty_owner = "& ".join(o.strip() for o in owner_list)
        clean_owner = _clean_whitespace(dirty_owner)
        if dirty_owner != clean_owner:
            is_multi_entity = True
        return OwnerData(clean_owner, is_multi_entity)


class MailingData(NamedTuple):
    line1: Optional[Line1]
    line2: Optional[Line2]
    line3: Optional[Line3]

    @classmethod
    def from_raw_general(cls, data: list[Tag | NavigableString]):
        return MailingData(None, None, None)

    @classmethod
    def from_raw_tax(cls, data: list[Tag | NavigableString]):
        address_list = _clean_tags(data)
        if len(address_list) == 3:
            line1 = parse.line1(address_list[0])
            line2 = parse.line2(address_list[1])
            line3 = parse.line3(address_list[2])
        elif not address_list:
            line1 = line2 = line3 = None
        else:
            breakpoint()
            raise NotImplementedError("I haven't dealt with this yet")

        return MailingData(line1, line2, line3)


class MailingAddress(NamedTuple):
    owner: OwnerData
    mailing: MailingData


def _clean_tags(content: list[Tag | NavigableString]) -> list[str]:
    return [str(tag) for tag in content if isinstance(tag, NavigableString)]


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text)
