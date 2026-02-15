from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Protocol


@dataclass
class ParsedTransaction:
    date: date
    time: time
    action: str  # "buy" or "sell"
    ticker: str
    quantity: int
    price: Decimal
    value: Decimal
    fee: Decimal
    contract_note: str | None = None


class Parser(Protocol):
    @staticmethod
    def can_handle(filename: str, content: bytes) -> bool: ...

    @staticmethod
    def parse(filename: str, content: bytes) -> tuple[list[ParsedTransaction], list[str]]: ...


PARSERS: list[type[Parser]] = []


def register(cls: type[Parser]) -> type[Parser]:
    PARSERS.append(cls)
    return cls
