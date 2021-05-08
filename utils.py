from typing import Any, Union


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
