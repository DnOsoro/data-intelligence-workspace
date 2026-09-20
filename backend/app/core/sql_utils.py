import re


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str) -> str:
    """
    Validate a SQL identifier used for internal DuckDB table/column names.

    Only standard alphanumeric identifiers beginning with a letter or
    underscore are allowed.
    """
    if not _IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(
            f"Invalid SQL identifier: {identifier!r}"
        )

    return identifier