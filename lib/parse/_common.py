# fmt: off
import os
from lark import Lark

def _make_parser(name: str):
    dir = os.path.split(__file__)[0]
    folder = "grammar"
    file = name + ".lark"
    absolute_path = os.path.join(dir, folder, file)
    with open(absolute_path, "r") as f:
        grammar = f.read()
    return Lark(grammar, start="start", parser="earley")


def _extract_zip_code(text: str) -> str:
    """ Naively parses the 5-digit zip code from codes like 15235 and 15235-5033"""
    return text.split("-")[0]

