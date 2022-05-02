__all__ = ["general_info", "tax_info"]
# Todo: Client pooling
import httpx

GENERALINFO = "GeneralInfo"
BUILDING = "Building"
TAX = "Tax"
SALES = "Sales"
IMAGES = "Images"
COMPS = "Comps"
APPEAL = "Appeal"
MAP = "Map"


def general_info(parcel_id: str) -> httpx.Response:
    return _county_property_assessment(parcel_id, section=GENERALINFO)


def tax_info(parcel_id: str) -> httpx.Response:
    return _county_property_assessment(parcel_id, section=TAX)


def _county_property_assessment(parcel_id: str, section: str) -> httpx.Response:
    COUNTY_REAL_ESTATE_URL = "https://www2.county.allegheny.pa.us/RealEstate/"
    URL_ENDING = ".aspx?"
    search_parameters = {
        "ParcelID": parcel_id,
        "SearchType": 3,
        "SearchParcel": parcel_id,
    }
    return httpx.get(
        (COUNTY_REAL_ESTATE_URL + section + URL_ENDING),
        params=search_parameters,
        timeout=5,
        follow_redirects=True,
    )
