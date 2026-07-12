""" Shared environment output formatting properties. """

SETTING_COLUMN_WIDTH = 40
PRINT_COLOR = "\033[32m"
COLOR_RESET = "\033[0m"

SENSITIVE_ENV_KEYWORDS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PASS",
    "KEY",
    "CREDENTIAL",
    "AUTH",
)


def display_env_value(name: str, value: object) -> str:
    """Return a log-safe string for environment values."""
    upper_name = name.upper()
    if any(keyword in upper_name for keyword in SENSITIVE_ENV_KEYWORDS):
        return "[HIDDEN]"

    return str(value)
