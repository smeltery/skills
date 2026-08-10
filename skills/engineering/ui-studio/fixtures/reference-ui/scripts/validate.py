#!/usr/bin/env python3
"""Validate the disposable fixture without external packages."""

from html.parser import HTMLParser
from pathlib import Path


class FixtureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_main = False
        self.buttons = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "main":
            self.has_main = True
        if tag == "button":
            self.buttons += 1


source = (Path(__file__).resolve().parent.parent / "public" / "index.html")
parser = FixtureParser()
parser.feed(source.read_text(encoding="utf-8"))
assert parser.has_main, "fixture requires a main landmark"
assert parser.buttons >= 2, "fixture requires two interactions"
print("Fixture validation passed.")
