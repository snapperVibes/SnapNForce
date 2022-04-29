# fmt: off
from lark import Transformer, LarkError
from lib.parse._common import _make_parser, _extract_zip_code
from lib.types import DeliveryAddressLine, LastLine

mortgage_parser = _make_parser("mortgage")

class MortgageTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._attn = None
        self._number = None
        self._street = None
        self._is_pobox = None
        self._secondary = None

    def street(self, v):
        self._street = " ".join(w for w in v)  # word for word in value
        return v

    def attention_subject(self, v):
        self._attn = " ".join(w for w in v)
        return v

    def pobox_number(self, v):
        self._number = " ".join(w for w in v)
        return v

    def secure_unit(self, v):
        self._is_pobox = True
        return v

    def building_number(self, v):
        self._number = " ".join(w for w in v)
        return v

    def secondary(self, v):
        # THIS ONE IS DIFFERENT: IT RETURNS A LIST OF TREES.
        #  Each tree has a subtree for each role (
        self._secondary = " ".join(
            str(tree.children[0]) for tree in
            (tree for tree in v)
        )
        return v

    def start(self, v):
        # This is the one that gives the output
        if not self._is_pobox:
            self._is_pobox = False
        if self._is_pobox:
            assert self._street is None
            self._street = "PO BOX"
        return DeliveryAddressLine(
            is_pobox=self._is_pobox,
            attn=self._attn,
            number=self._number,
            street=self._street,
            secondary=self._secondary
        )

# Todo: Research standalone parser
def mortgage_delivery_address_line(text: str) -> DeliveryAddressLine:
    try:
        tree = mortgage_parser.parse(text)
        return MortgageTransformer().transform(tree)
    except LarkError as err:
        msg = str(err)
        print(msg)
        # If this goes wrong, it is likely our grammar is wrong.
        #  Let's log a detailed error message so fixing it is easy.
        raise

def mortgage_last_line(city_state: str, zip: str) -> LastLine:
    city, state = city_state.split("  ")
    zip = _extract_zip_code(zip)
    return LastLine(city=city, state=state, zip=zip)
