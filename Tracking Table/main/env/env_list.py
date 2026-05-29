""" Environment variable list parser. """

import os
from .env_properties import COLOR_RESET, PRINT_COLOR, SETTING_COLUMN_WIDTH

def env_list(name: str, default: list[str] | None = None, *, sep: str = ",") -> list[str]:
    raw_value = os.getenv(name)

    # Return the default value if the variable is not set and no default is provided
    if raw_value is None:
        if default is None:
            raise RuntimeError(f"{name} setting value is required! ")

        return default

    # Return the list of values stripped of whitespace
    value = [item.strip() for item in raw_value.split(sep) if item.strip()]
    print(f"{name:<{SETTING_COLUMN_WIDTH}} -> {PRINT_COLOR}{value}{COLOR_RESET}")
    return value