__all__ = ["general_html_content", "mortgage_html_content"]
# fmt: off
from typing import AnyStr, Optional
from bs4 import BeautifulSoup, Tag, NavigableString

# HTML Elements
from lib.parse.exceptions import HtmlParsingError

SPAN = "span"
TR = "tr"

# Allegheny County Property Assessment span ids
PARCEL_ADDRESS = "BasicInfo1_lblAddress"
OWNER_NAME = "BasicInfo1_lblOwner"
OWNER_MAILING = "lblChangeMail"
ADDRESS = "BasicInfo1_lblAddress"
MUNICIPALITY = "BasicInfo1_lblMuni"
PARCEL_ID_LoB = "BasicInfo1_lblParcelID"
MORTGAGE = "lblMortgage"
TAXINFO = "lblTaxInfo"

_ScrapedData = Optional[list[Tag | NavigableString]]

def _soupify(raw_html: str) -> BeautifulSoup:
    return BeautifulSoup(raw_html, "html.parser")

def general_html_content(html_: AnyStr) -> tuple[_ScrapedData, _ScrapedData, _ScrapedData]:
    soup = _soupify(html_)
    parcel_mailing = _find_parcel_mailing(soup)
    owners = _find_owner_names(soup)
    mailing = _find_owner_mailing(soup)
    if (owners is None) or (mailing is None):
        raise HtmlParsingError
    return parcel_mailing, owners, mailing

def mortgage_html_content(html_: AnyStr) -> tuple[_ScrapedData, _ScrapedData]:
    soup = _soupify(html_)
    address = _find_mortgage_mailing(soup)
    try:
        owners = address[0]
        mailing = address[1:]
    except IndexError:
        raise HtmlParsingError
    return [owners], mailing

def _find_parcel_mailing(soup: BeautifulSoup) -> _ScrapedData:
    '''
    Extracts only the parcel's mailing address from the general page
    '''
    return soup.find(SPAN, id=PARCEL_ADDRESS).contents

def _find_owner_names(soup: BeautifulSoup) -> _ScrapedData:
    return soup.find(SPAN, id=OWNER_NAME).contents

def _find_owner_mailing(soup: BeautifulSoup) -> _ScrapedData:
    return soup.find(SPAN, id=OWNER_MAILING).contents

def _find_mortgage_mailing(soup: BeautifulSoup) -> _ScrapedData:
    return soup.find(SPAN, id=MORTGAGE).contents
