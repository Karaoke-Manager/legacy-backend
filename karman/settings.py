__all__ = ["Settings"]

import os
from datetime import timedelta
from functools import lru_cache
from logging.config import dictConfig
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import yaml
from jose.constants import Algorithms
from pydantic import BaseSettings, Extra, Field, FilePath
from pydantic.env_settings import SettingsSourceCallable

from karman.util.settings import (
    ConfigFileSettingsSource,
    MySQLDsn,
    PostgresDsn,
    SQLiteDsn,
)

ENV_PREFIX = os.getenv("KARMAN_ENV_PREFIX", "KARMAN_")
ENV_FILE_ENCODING = os.getenv(f"{ENV_PREFIX}ENV_ENCODING")
ENV_FILENAME = os.getenv(f"{ENV_PREFIX}ENV_FILE", ".env")
SECRETS_DIR = os.getenv(f"{ENV_PREFIX}SECRETS_DIR", "/run/secrets")
CONFIG_FILE_ENCODING = os.getenv(f"{ENV_PREFIX}CONFIG_ENCODING")
CONFIG_FILENAMES = [
    filename.strip()
    for filename in os.getenv(
        f"{ENV_PREFIX}CONFIG", "config.yaml,config.yml,config.json"
    ).split(",")
]


class Settings(BaseSettings):
    """
    The global settings for the Karman API backend.

    Using the settings
    ==================
    In your code you can use ``karman.config.settings``, an already initialized object
    containing the actual settings values. Use it via ``Settings.instance()``.

    Configuration sources
    =====================
    The ``Settings`` class reads configuration values from three different places. In
    increasing order of precedence:

    0. (Settings defaults)
    1. A .env file
    2. Environment variables
    3. Secrets folder
    4. A JSON or YAML configuration file

    Chosing Config Sources
    ======================

    The configuration sources themselves can be configured via the environment:

    ``KARMAN_ENV_PREFIX``
        A prefix for **all** other environment variables used for configuration.
        Default: ``KARMAN_``
    ``{prefix}ENV_FILE`` and ``{prefix}ENV_FILE_ENCODING``
        The path and encoding of a .env file from which additional configuration
        variables will be loaded. Default: ``.env``
    ``{prefix}SECRETS_DIR``
        A directory containing files that are named like the configuration values (with
        the configured prefix). The content of the files is used as configuration value.
    ``{prefix}CONFIG`` and ``{prefix}CONFIG_ENCODING``
        The path and encoding of a JSON or YAML file containing configuration values.
        You can specify multiple comma-separated values. The first file found will be
        used. Multiple files will not be merged.
        Default: ``config.yaml,config.yml,config.json``
    """

    debug: bool = Field(
        True,
        title="Debug Mode Switch",
        description="Enables or disables the debug mode. The debug mode includes some "
        "additional checks that may impact performance. Also it may display sensitive "
        "debug information when errors occur.",
    )
    logging_config: Union[FilePath, Dict[str, Any], None] = Field(
        None,
        title="Logging Configuration",
        description="Either the path to a JSON or YAML file according to the Logging "
        "Config Dict Schema or an embedded dictionary that is used to configure "
        "logging.",
    )
    app_name: str = Field(
        "Karman API",
        description="The name of the application. This value may be visible in the UI.",
    )
    db_url: Union[SQLiteDsn, MySQLDsn, PostgresDsn] = Field(
        "sqlite+aiosqlite:///db.sqlite",
        title="Database connection string",
        description="A SQLAlchemy database connection URL.",
    )
    jwt_issuer: str = Field(
        "Karman",
        title="Issuer of JWT access tokens.",
        description="The issuer is included in tokens and can be used to differentiate "
        "tokens issued by different installations.",
    )
    jwt_algorithm: str = Field(
        Algorithms.HS256,
        title="JWT Algorithm",
        description="Signing algorithm used for OAuth2 access tokens.",
    )
    jwt_secret_key: str = Field(
        ...,
        min_length=20,
        title="JWT Secret Key",
        description="A secret value used to encode and decode access tokens.",
    )
    jwt_validity_period: timedelta = Field(
        default=timedelta(minutes=60),
        title="JWT Validity Period",
        description="The duration for which an access token is valid.",
    )

    class Config:
        allow_population_by_field_name = True
        validate_all = True
        validate_assignment = True
        allow_mutation = False
        extra = Extra.forbid

        env_prefix = ENV_PREFIX
        env_nested_delimiter = "__"
        env_file_encoding = ENV_FILE_ENCODING
        env_file = ENV_FILENAME
        config_file_encoding = CONFIG_FILE_ENCODING
        config_files = CONFIG_FILENAMES
        secrets_dir = SECRETS_DIR if Path(SECRETS_DIR).exists() else None

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                ConfigFileSettingsSource(cls.config_files, cls.config_file_encoding),
                file_secret_settings,
                env_settings,
            )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Load Default Logging Config
        with open("logging.yml", "r") as file:
            dictConfig(yaml.safe_load(file))
        # Load User Logging Config
        if isinstance(self.logging_config, dict):
            logging_config = self.logging_config
        elif isinstance(self.logging_config, Path):
            with self.logging_config.open("r") as file:
                logging_config = yaml.safe_load(file)
        else:
            logging_config = None
        if logging_config:
            dictConfig(logging_config)

    @classmethod
    @lru_cache
    # TODO: Return 'Self' in Python 3.11
    def instance(cls) -> "Settings":
        """
        Returns the global ``Settings`´ instance.
        """
        return cls()
