from lib.parse import general_street_line as parse
from app.schemas import Line1


def test_general():
    a = parse("304\xa0STATION\xa0ST\xa0")
    e = Line1(is_pobox=False, attn=None, number="304", street="STATION ST")
    assert a == e

def test_pobox():
    a = parse("PO BOX 48\xa0")
    e = Line1(is_pobox=True, attn=None, number="48", street="PO BOX")
    assert a == e


# def test_room():
#     a = parse("542\xa0FORBES\xa0AVE\xa0RM\xa0347\xa0")
#     e = Line1(is_pobox=False, attn=None, number="304", street="JACKS RUN RD", room="304")
