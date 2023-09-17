import re

__all__ = ['check_storehouse_nothing_found_literal']

_pattern_nothing_found = re.compile('не\s+удалось\s+ничего\s+подобрать', re.IGNORECASE | re.UNICODE |
                                    re.MULTILINE)


def check_storehouse_nothing_found_literal(lines: list[str] | None) -> bool:
    return any(_check_storehouse_nothing_found_literal(line) for line in lines) if lines else False


def _check_storehouse_nothing_found_literal(line: str | None) -> bool:
    return bool(_pattern_nothing_found.search(line)) if line else False
