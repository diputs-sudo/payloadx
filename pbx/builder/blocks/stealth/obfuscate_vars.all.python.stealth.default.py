# builder/blocks/stealth/obfuscate_vars.all.python.stealth.default.py

"""
Very naive variable-renamer (demo only).
"""

import re, random, string

METADATA = {
    "name":     "obfuscate_vars",
    "platform": "all",
    "language": "python",
    "category": "stealth",
    "variant":  "default",
    "args":     ["code"],
    "returns":  "str",
}

_identifier = re.compile(r"\\b([a-zA-Z_][a-zA-Z0-9_]*)\\b")

def _rand_name(n=8):
    return "".join(random.choice(string.ascii_letters) for _ in range(n))

def generate(code: str) -> str:
    # Find unique identifiers short of Python keywords
    keywords = set(__import__("keyword").kwlist)
    ids = {m.group(1) for m in _identifier.finditer(code)} - keywords
    mapping = {name: _rand_name() for name in ids}
    for old, new in mapping.items():
        code = re.sub(rf"\\b{old}\\b", new, code)
    return code
