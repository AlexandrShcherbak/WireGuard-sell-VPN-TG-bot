import re


def is_valid_wg_name(name: str) -> bool:
    return bool(re.fullmatch(r'[a-zA-Z0-9_-]{3,32}', name))
