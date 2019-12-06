from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import IO


@dataclass
class Printer:
    file: IO[str] = sys.stdout
    tab: str = "\t"
    level: int = 0

    @property
    def indentation(self) -> str:
        return self.tab * self.level

    def print(self, s: str):
        print(self.indentation + s, file=self.file)

    @property
    def indented(self) -> Printer:
        return Printer(self.file, self.tab, self.level + 1)
