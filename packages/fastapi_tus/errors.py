__all__ = [
    "TusError",
    "TusUploadNotFoundError",
    "TusUploadGoneError",
    "TusPermissionDeniedError",
]


class TusError(Exception):
    pass


class TusUploadNotFoundError(Exception):
    pass


class TusPermissionDeniedError(Exception):
    pass


class TusUploadGoneError(Exception):
    pass
