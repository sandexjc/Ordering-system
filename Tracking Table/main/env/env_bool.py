""" Environment variable boolean parser. """

import os
from .env_properties import COLOR_RESET, PRINT_COLOR, SETTING_COLUMN_WIDTH

def env_bool(name: str, default: bool = False, *, required: bool = False) -> bool:
    raw_value = os.getenv(name)

    # Default to False if the variable is not set and not required
    if raw_value is None:
        if required:
            raise RuntimeError(f"{name} setting is required! ")

        return default

    # Parse the boolean value
    bool_map = {
        "1": True,
        "true": True,
        "yes": True,
        "on": True,
        "0": False,
        "false": False,
        "no": False,
        "off": False,
    }

    key = raw_value.strip().lower()
    if key not in bool_map:
        raise RuntimeError(
            f"{name} setting value must be one of: {', '.join(bool_map.keys())}. Got: {raw_value} !"
        )

    value = bool_map[key]
    print(f"{name:<{SETTING_COLUMN_WIDTH}} -> {PRINT_COLOR}{value}{COLOR_RESET}")
    return value