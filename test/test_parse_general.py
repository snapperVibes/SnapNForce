# fmt: off
from lib.parse import general_delivery_address_line as parse
from app.schemas import DeliveryAddressLine


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
