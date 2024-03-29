# fmt: off
from lark import Transformer, LarkError
from lib.parse._common import _make_parser, _extract_zip_code
from lib.parse.exceptions import HtmlParsingError
from lib.parse.models import DeliveryAddressLine, LastLine
import re

general_parser = _make_parser("general")

class GeneralTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._attn = None
        self._number = None
        self._street = None
        self._type = None
        self._is_pobox = None
        self._secondary = None

    def building_number(self, v):
        self._number = " ".join(w for w in v)
        return v

    def street(self, v):
        self._street = " ".join(w for w in v)
        return v

    def type(self, v):
        self._type = " ".join(w for w in v)
        return v

    def room(self, v):
        self._ = " ".join(w for w in v)
        return v

    def secure_unit(self, v):
        self._is_pobox = True
        return v

    def pobox_number(self, v):
        self._number = " ".join(w for w in v)
        return v

    def secondary(self, v):
        self._secondary = " ".join(
            str(tree.children[0]) for tree in
            (tree for tree in v)
        )
        return v

    def start(self, v):
        if not self._is_pobox:
            self._is_pobox = False
        if self._is_pobox:
            assert self._street is None
            self._street = "PO BOX"
        street = [self._street]
        if self._type:
            street.append(self._type)
        return DeliveryAddressLine(
            is_pobox=self._is_pobox,
            street=" ".join(street),
            number=self._number,
            attn=self._attn,
            secondary=self._secondary
        )


def general_delivery_address_line(text: str) -> DeliveryAddressLine:
    try:
        tree = general_parser.parse(text)
        return GeneralTransformer().transform(tree)
    except LarkError as err:
        print("TEXT", text, sep="\t")
        print(str(err))
        raise


def general_city_state_zip(text: str) -> LastLine:
    # This function parses both the property address    (PITTSBURGH,\xa0PA\xa015235)
    #  and the owner mailing                            (PITTSBURGH\xa0,\xa0PA\xa015235-5033)
    city, state, zip_ = (x for x in text.split("\xa0") if x != ",")
    return LastLine(city=city.rstrip(","), state=state, zip=_extract_zip_code(zip_))
 
