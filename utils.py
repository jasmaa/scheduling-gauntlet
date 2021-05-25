from typing import Any, Union
import re
import uuid


def parse_int(v: Any) -> Union[int, None]:
    """Tries to parse to int

    :param v: Value to parse to int
    :param type: Any

    :return: Parsed int or None if error occured
    :rtype: Union[int, NoneType]
    """
    try:
        return int(v)
    except ValueError:
        return None


email_pattern = re.compile("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")


def validate_email(email: str) -> bool:
    """Checks if `email` is an email

    :param email: Email
    :param type: str

    :return: Whether email is an email
    :rtype: bool
    """

    return email_pattern.match(email) != None


def generate_code() -> str:
    """Generates password reset code

    :return: Password reset code
    :rtype: str
    """

    return str(uuid.uuid4())
