# import pytest
#
# import app
# from lib.parse import line1 as parse
# from lib.parse.types import Line1
# from lark.exceptions import UnexpectedEOF
#
#
# def test_street():
#     a = parse("MORELLE AVE")
#     e = Line1(is_pobox=False, attn=None, number=None, street="MORELLE AVE")
#     assert a == e
#
# def test_number_street():
#     a = parse("569 HELENA ST")
#     e = Line1(is_pobox=False, attn=None, number="569", street="HELENA ST")
#     assert a == e
#
# def test_attn_pobox():
#     a = parse("ATTENTION: BILLS RECIEVED PO BOX 9201")
#     e = Line1(is_pobox=True, attn="BILLS RECIEVED", number="9201", street=None)
#     assert a == e
#
# def test_pobox_attn():
#     a = parse("PO BOX 1820 ATTN: B6-YM07-01-7")
#     e = Line1(is_pobox=True, attn="B6-YM07-01-7", number="1820", street=None)
#
#
#
#
#
#
# def test_attn_pobox():
#     a = parse("ATTENTION: BILLS RECIEVED PO BOX 9201")
#     e = Line1(is_pobox=True, attn="BILLS RECIEVED", number='9201', street=None)
#     assert a == e
