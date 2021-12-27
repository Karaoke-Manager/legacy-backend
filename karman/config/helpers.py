__all__ = ["ConfigFileSettingsSource", "SQLiteDsn", "PostgresDsn", "MySQLDsn"]

from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

import yaml
from pydantic import AnyUrl, BaseSettings


class ConfigFileSettingsSource:
    """
    A simple configuration source reading from a JSON file.
    """

    __slots__ = ("file", "encoding")

    def __init__(
        self,
        file: Sequence[Union[Path, str]] = None,
        encoding: Optional[str] = None,
    ):
        self.file = file if file else []
        self.encoding = encoding

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        for path in self.file:
            file = Path(path).expanduser()
            if file.exists():
                with file.open("r", encoding=self.encoding) as stream:
                    # Since YAML is a superset of JSON this can process JSON
                    # configs as well.
                    data = yaml.safe_load(stream)
                    assert isinstance(data, dict)
                    return data
        return {}


# FIXME: This requires Pydantic 1.9. The one below is a temporary fix.
# class SQLiteDsn(AnyUrl):
#     allowed_schemes = {"sqlite"}
#     host_required = False
SQLiteDsn = str


class PostgresDsn(AnyUrl):
    # TODO: Add allowed drivers here
    allowed_schemes = {"postgres", "postgresql"}
    user_required = True


class MySQLDsn(AnyUrl):
    # TODO: Add allowed drivers here
    allowed_schemes = {"mysql", "mariadb"}
    user_required = True
