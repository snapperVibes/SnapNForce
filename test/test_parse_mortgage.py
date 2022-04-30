import pytest

import app
from lib.parse import mortgage_delivery_address_line as parse
from lib.parse._types import DeliveryAddressLine
from lark.exceptions import UnexpectedEOF

# test format
#   def test_whatever():
#       a<ctual> = p("PO BOX: EXAMPLE")
#       e<xpected> = Line1(is_pobox=True, attn=None, number='EXAMPLE', street=None)
#       assert a == e
#
# Play with the grammer here:
#  https://www.lark-parser.org/ide/


def test_001():
    a = parse("ATTENTION: BILLS RECIEVED PO BOX 9201")
    e = DeliveryAddressLine(is_pobox=True, attn="BILLS RECIEVED", number="9201", street="PO BOX")
    assert a == e


def test_002():
    a = parse("569 HELENA ST")
    e = DeliveryAddressLine(is_pobox=False, attn=None, number="569", street="HELENA ST")
    assert a == e


def test_003():
    a = parse("SELECT PORTFOLIO SERVICING - DISBURSEMENT UNIT 901 CORPORATE CENTER")
    e = DeliveryAddressLine(
        is_pobox=False,
        attn="SELECT PORTFOLIO SERVICING - DISBURSEMENT UNIT",
        number="901",
        street="CORPORATE CENTER",
    )
    assert a == e


def test_004():
    a = parse("MORELLE AVE")
    e = DeliveryAddressLine(is_pobox=False, attn=None, number=None, street="MORELLE AVE")
    assert a == e


def test_005():
    a = parse("111 WESTPORT PLZ STE 1150")
    e = DeliveryAddressLine(
        is_pobox=False, attn=None, number="111", street="WESTPORT PLZ", secondary="STE 1150"
    )
    assert a == e


# def test_002():
#     a = parse("PO BOX: EXAMPLE 123")
#     e = Line1(is_pobox=True, attn=None, number='EXAMPLE 123', street=None)
#     assert a == e
#
# def test_003():
#     a = parse("PO BOX EXAMPLE")
#     e = Line1(is_pobox=True, attn=None, number='EXAMPLE', street=None)
#     assert a == e
#
# def test_004():
#     a = parse("P O BOX EXAMPLE 123")
#     e = Line1(is_pobox=True, attn=None, number='EXAMPLE 123', street=None)
#     assert a == e
#
# def test_005():
#     a = parse("P O BOX 123")
#     e = Line1(is_pobox=True, attn=None, number='123', street=None)
#     assert a == e
#
# def test_007():
#     a = parse("ATTN: FELLOW HUMANS PO BOX EXAMPLE")
#     e = Line1(is_pobox=True, attn="FELLOW HUMANS", number='EXAMPLE', street=None)
#     assert a == e
#
# def test_008():
#     a = parse("PO BOX 1234 ATTN: NAME")
#     e = Line1(is_pobox=True, attn="NAME", number='1234', street=None)
#     assert a == e

# Everything after this is based on real examples


#
# def test_010():
#     a = parse("MORELLE AVE")
#     e = Line1(is_pobox=False, attn=None, number=None, street="MORELLE AVE")
#     assert a == e
#
#
# # From here on out tests will be based on errors
# def test_ampersand():
#     a = parse("C/O MELVIN J WOJTOWICZ & BONNIE E ALEXANDER TRUSTEES 706 FORREST OAKS TRL")
#     e = Line1(is_pobox=False, attn="MELVIN J WOJTOWICZ & BONNIE E ALEXANDER TRUSTEES", number='706', street="FORREST OAKS TRL")
#     assert  a == e


# def test_009():
#     a = parse("PO BOX 1234 ATTN: NAME")
#     e = Line1(is_pobox=True, attn="NAME", number='1234', street=None)
#     assert a == e

# def test_0010():
#     a = parse("PO BOX 1234 ATTN: 5678")
#     e = Line1(is_pobox=True, attn="5678", number='1234', street=None)
#     assert a == e


def test_f001():
    with pytest.raises(UnexpectedEOF):
        parse("")


# def test_f002():
#     with pytest.raises(Exception):
#         parse("ATTN: HELLO")
#
#
#
#
