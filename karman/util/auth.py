import binascii
from base64 import b64decode
from typing import Tuple

from fastapi.security.utils import get_authorization_scheme_param


def decode_basic_auth(header: str) -> Tuple[str, str]:
    """
    Decodes the value of an ``Authorization`` header expecting HTTP Basic Auth
    credentials.
    :param header: The header value (including the leading 'Basic' prefix.
    :return: A tuple of username and password encoded in the header.
    :raises ValueError: If the provided value cannot successfully be decoded as HTTP
                        Basic Auth header value.
    """
    scheme, param = get_authorization_scheme_param(header)
    if scheme.lower() != "basic":
        raise ValueError("authorization scheme mismatch")
    try:
        data = b64decode(param).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise ValueError("base64 decode failed")
    username, separator, password = data.partition(":")
    if not separator:
        raise ValueError("invalid format")
    return username, password
