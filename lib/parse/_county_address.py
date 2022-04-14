import os
import re

import lark.exceptions
from lark import Lark, Transformer, LarkError
from lib.parse.types import Line1, Line2, Line3


def _make_parser(name: str):
    dir = os.path.split(__file__)[0]
    folder = "grammar"
    file = name + ".lark"
    absolute_path = os.path.join(dir, folder, file)
    with open(absolute_path, "r") as f:
        grammar = f.read()
    return Lark(grammar, start="start", parser="earley")


line1_parser = _make_parser("line1")


class LineOneTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._attn = None
        self._number = None
        self._street = None
        self._is_pobox = None

    def street(self, v):
        self._street = " ".join(w for w in v)
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
    # def just_a_number_building_number(self, v):
    #     self._number = " ".join(w for w in v)
    #     return v
    #
    # def non_greedy_potential_words_ending_in_a_building_number(self, v):
    #     self._number = " ".join(w for w in v)
    #     return v

    def start(self, v):
        # This is the one that gives the output
        if not self._is_pobox:
            self._is_pobox = False
        return Line1(
            is_pobox=self._is_pobox,
            attn=self._attn,
            number=self._number,
            street=self._street,
        )


# Todo: probably should use the standalone parser
def line1(text: str) -> Line1:
    try:
        tree = line1_parser.parse(text)
        return LineOneTransformer().transform(tree)
    except LarkError as err:
        msg = str(err)
        print(msg)
        # If this goes wrong, it is likely our grammar is wrong.
        #  Let's log a detailed error message so fixing it is easy.
        raise


def line2(text: str) -> Line2:
    return Line2(*text.split("  "))


_zip_code = re.compile(r"(\d{5})(-\d{4})?")


def line3(text: str) -> Line3:
    m = re.match(_zip_code, text)
    if m is None:
        raise RuntimeError("Could not parse zipcode")
    return Line3(m.group(1))
