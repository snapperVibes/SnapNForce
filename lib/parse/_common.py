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

# Todo: decide whether to use Regex or string methods
def _extract_zip_code(text: str) -> str:
    return text.split("-")[0]

# _zip_code = re.compile(r"(\d{5})(-\d{4})?")
