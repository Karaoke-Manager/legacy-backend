__all__ = ["ConfigFileSettingsSource", "SQLiteDsn", "PostgresDsn", "MySQLDsn"]

from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

import yaml
from pydantic import AnyUrl, BaseSettings


class ConfigFileSettingsSource:
    """
    A simple configuration source reading from a JSON file.

    See https://pydantic-docs.helpmanual.io/usage/settings/#customise-settings-sources.
    """

    __slots__ = ("file", "encoding")

    def __init__(
        self,
        file: Optional[Sequence[Union[Path, str]]] = None,
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


class SQLiteDsn(AnyUrl):
    """
    A SQLite connection string.
    """

    allowed_schemes = {"sqlite+aiosqlite"}
    host_required = False  # file URLs do not have a host component


class PostgresDsn(AnyUrl):
    """
    A PostgreSQL connection string.
    """

    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}
    user_required = True


class MySQLDsn(AnyUrl):
    """
    A MySQL/MariaDB connection string.
    """

    allowed_schemes = {"mysql+aiomysql", "mariadb+aiomysql"}
    user_required = True
