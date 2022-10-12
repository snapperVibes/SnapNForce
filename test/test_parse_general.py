# fmt: off
from lib.parse import general_delivery_address_line as parse, general_city_state_zip
from app.schemas import DeliveryAddressLine
from lib.parse.models import LastLine


def test_general():
    a = parse("304\xa0STATION\xa0ST\xa0")
    e = DeliveryAddressLine(is_pobox=False, attn=None, number="304", street="STATION ST")
    assert a == e

def test_pobox():
    a = parse("PO BOX 48\xa0")
    e = DeliveryAddressLine(is_pobox=True, attn=None, number="48", street="PO BOX")
    assert a == e

def test_secondary():
    a = parse("12\xa0FEDERAL\xa0ST\xa0STE\xa0400\xa0")
    e = DeliveryAddressLine(is_pobox=False, attn=None, number="12", street="FEDERAL ST", secondary="STE 400")
    assert a == e

# def test_room():
#     a = parse("542\xa0FORBES\xa0AVE\xa0RM\xa0347\xa0")
#     e = Line1(is_pobox=False, attn=None, number="304", street="JACKS RUN RD", room="304")

### Last line ###

def test_property_address_city_state_zip():
    a = general_city_state_zip("PITTSBURGH,\xa0PA\xa015235")
    e = LastLine(city="PITTSBURGH", state="PA", zip="15235")
    assert a == e

def test_owner_mailing_city_state_zip():
    a = general_city_state_zip("PITTSBURGH\xa0,\xa0PA\xa015235-5033")
    e = LastLine(city="PITTSBURGH", state="PA", zip="15235")
    assert a == e



