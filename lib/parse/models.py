from pydantic import BaseModel, validator
from typing import Optional

# Names were chosen in regard to USPS's Publication 28 - Postal Addressing Standards
#  Delivery Address Line:    https://pe.usps.com/text/pub28/28c2_012.htm
#  Last line of the Address: https://pe.usps.com/text/pub28/28c2_006.htm


class DeliveryAddressLine(BaseModel):
    is_pobox: Optional[bool]
    attn: Optional[str]
    number: Optional[str]
    street: Optional[str]
    secondary: Optional[str]


class LastLine(BaseModel):
    city: str
    state: str
    zip: str
