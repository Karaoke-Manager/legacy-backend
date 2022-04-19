import binascii
from base64 import b64decode
from typing import Tuple

from fastapi.security.utils import get_authorization_scheme_param


def decode_basic_auth(header: str) -> Tuple[str, str]:
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
