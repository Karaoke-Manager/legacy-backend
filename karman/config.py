__all__ = ["settings"]

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from pydantic import BaseSettings, Extra, Field
from pydantic.env_settings import SettingsSourceCallable

ENV_PREFIX = os.getenv("KARMAN_ENV_PREFIX", "KARMAN_")
ENV_FILENAME = os.getenv(f"{ENV_PREFIX}ENV_FILE", ".env")
ENV_FILE_ENCODING = os.getenv(f"{ENV_PREFIX}ENV_ENCODING")
SECRETS_DIR = os.getenv(f"{ENV_PREFIX}SECRETS_DIR", "/run/secrets")
JSON_FILENAME = os.getenv(f"{ENV_PREFIX}CONFIG", "config.json")
JSON_FILE_ENCODING = os.getenv(f"{ENV_PREFIX}CONFIG_ENCODING")


class JsonSettingsSource:
    """
    A simple configuration source reading from a JSON file.
    """

    __slots__ = ("json_file", "json_file_encoding")

    def __init__(
        self,
        json_file: Union[Path, str, None] = None,
        json_file_encoding: Optional[str] = None,
    ):
        self.json_file = json_file
        self.json_file_encoding = json_file_encoding

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        if self.json_file is None:
            return {}
        file = Path(self.json_file).expanduser()
        if file.exists():
            return json.loads(file.read_text(self.json_file_encoding))  # type: ignore
        else:
            return {}


class Settings(BaseSettings):
    """
    The global settings for the Karman API backend.

    Using the settings
    ==================
    In your code you can use ``karman.config.settings``, an already initialized object
    containing the actual settings values. Use it like so:

    >>> settings.app_name
    'Karman API'

    Configuration sources
    =====================
    The ``Settings`` class reads configuration values from three different places. In
    increasing order of precedence:

    0. (Settings defaults)
    1. A .env file
    2. Environment variables
    3. Secrets folder
    4. A JSON configuration file

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
        The path and encoding of a JSON file containing configuration values.
        Default: ``config.json``
    """

    app_name: str = Field(
        "Karman API",
        description="The name of the application. This value may be visible in the UI.",
    )
    debug: bool = Field(
        True,
        title="Enable Debug Mode",
        description="Enables or disables the debug mode. The debug mode includes some "
        "additional checks that may impact performance. Also it may display sensitive "
        "debug information when errors occur.",
    )

    class Config:
        allow_population_by_field_name = True
        validate_all = True
        validate_assignment = True
        allow_mutation = False
        extra = Extra.forbid

        env_prefix = ENV_PREFIX
        env_nested_delimiter = "__"
        env_file = ENV_FILENAME
        env_file_encoding = ENV_FILE_ENCODING
        json_file = JSON_FILENAME
        json_file_encoding = JSON_FILE_ENCODING
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
                JsonSettingsSource(cls.json_file, cls.json_file_encoding),
                file_secret_settings,
                env_settings,
            )


settings = Settings()
