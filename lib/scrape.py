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
    


# Todo: make threadsafe
#  SNAPPERS: we're single threaded
_client = {"async": None}


def _get_async_client():
    client = _client.get("async")
    if client is None:
        # Todo: add explicit Turtle Creek headers
        client = _client["async"] = httpx.AsyncClient()
    return client


async def general_info(parcel_id: str) -> httpx.Response:
    return await _county_property_assessment(parcel_id, section=GENERALINFO)


async def tax_info(parcel_id: str) -> httpx.Response:
    return await _county_property_assessment(parcel_id, section=TAX)


async def _county_property_assessment(parcel_id: str, section: str) -> httpx.Response:
    COUNTY_REAL_ESTATE_URL = "https://www2.county.allegheny.pa.us/RealEstate/"
    URL_ENDING = ".aspx?"
    search_parameters = {
        "ParcelID": parcel_id,
        "SearchType": 3,
        "SearchParcel": parcel_id,
    }
    client = _get_async_client()
    return await client.get(
        (COUNTY_REAL_ESTATE_URL + section + URL_ENDING),
        params=search_parameters,
        timeout=5,
        follow_redirects=True,
    )
