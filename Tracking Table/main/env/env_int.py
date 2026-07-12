""" Environment variable integer parser. """

import os
from .env_properties import COLOR_RESET, PRINT_COLOR, SETTING_COLUMN_WIDTH, display_env_value


def env_int(name: str, default: int | None = None, *, required: bool = False) -> int | None:
    raw_value = os.getenv(name)

    # Return the default value if the variable is not set and is not required
    if raw_value is None:
        if required:
            raise RuntimeError(f"{name} setting value is required! ")

        return default

    # Parse and return the integer value
    value = int(raw_value.strip())
    print(
        f"{name:<{SETTING_COLUMN_WIDTH}} -> "
        f"{PRINT_COLOR}{display_env_value(name, value)}{COLOR_RESET}"
    )
    return value
