""" Environment variable string parser. """

import os
from .env_properties import COLOR_RESET, PRINT_COLOR, SETTING_COLUMN_WIDTH, display_env_value

def env_str(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    raw_value = os.getenv(name)

    # Return the default value if the variable is not set and is not required
    if raw_value is None:
        if required:
            raise RuntimeError(f"{name} setting value is required! ")

        return default

    # Return the value stripped of whitespace
    value = raw_value.strip()
    print(
        f"{name:<{SETTING_COLUMN_WIDTH}} -> "
        f"{PRINT_COLOR}{display_env_value(name, value)}{COLOR_RESET}"
    )
    return value