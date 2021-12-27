import http
import logging
import sys
from copy import copy
from typing import Any, Dict, Literal, Optional, Union

import click
from uvicorn.logging import TRACE_LOG_LEVEL  # type: ignore


class ColorFormatter(logging.Formatter):
    """
    A custom log formatter class (adapted from Uvicorn) that provides coloring
    support for arbitraty text replacements.

    Additionally if a log call includes an `extras={"color_message": ...}` it
    will be used for formatting the output, instead of the plain text message.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        color_fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Union[Literal["%"], Literal["{"], Literal["$"]] = "%",
        use_colors: Optional[bool] = None,
        colors: Optional[Dict[str, Dict[str, Any]]] = None,
        level_colors: Optional[Dict[int, Dict[str, Any]]] = None,
    ):
        """
        Initializes this ``ColorFormatter``.

        :param fmt: The default log format.
        :param color_fmt: A different log format to be used in coloring mode.
                          Defaults to ``fmt``.
        :param datefmt: The date format to be used for ``asctime``.
        :param style: The format style used in the log template.
        :param use_colors: Whether to enable colors or not. If left unspecified
                           we try to autodetect if we are running in a TTY.
        :param colors: The color specifiers for text replacements. Keys in this
                       dictionary are the names of text replacements. Values are
                       dictionaries consisting of parameters and values passed to
                       click.style.

                       Color specifiers can also contain the special key ``level``. If
                       set to ``True`` the respective text replacement will be colored
                       according to the log level.
        :param level_colors: A dictionary where the keys are log levels and the values
                             are color specifiers. For the default log levels a default
                             set of colors is provided that can be overridden by
                             specifying custom colors for a log level.
        """
        self.use_colors = (
            use_colors if use_colors in (True, False) else sys.stdout.isatty()
        )
        self.colors = colors or {}
        self.level_colors = {
            TRACE_LOG_LEVEL: {"fg": "blue"},
            logging.DEBUG: {"fg": "cyan"},
            logging.INFO: {"fg": "green"},
            logging.WARNING: {"fg": "yellow"},
            logging.ERROR: {"fg": "red"},
            logging.CRITICAL: {"fg": "bright_red"},
        } | (level_colors or {})
        color_fmt = color_fmt or fmt
        super().__init__(
            fmt=color_fmt if self.use_colors else fmt, datefmt=datefmt, style=style
        )

    def colorize(self, record: logging.LogRecord, attribute: str) -> None:
        """
        Replaces the ``attribute`` in ``record`` by a colored version according to the
        formatter's configuration.

        :param record: The record to be logged.
        :param attribute: The name of the attribute.
        """
        try:
            color = self._refine_color(record, copy(self.colors[attribute]))
            value = getattr(record, attribute)
            setattr(record, attribute, click.style(value, **color))
        except KeyError:
            pass

    def _refine_color(
        self, record: logging.LogRecord, color: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Selects the actual parameters for ``click.style`` according to a color
        specification. This can be overridden by subclasses to support their own special
        keys.

        :param record: The record to be logged.
        :param color: The color specification.
        """
        if color.pop("level", False):
            color = self.level_colors[record.levelno] | color
        return color

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        if self.use_colors:
            setattr(record_copy, "reset", click.style("", reset=True))
            for key in ["name", "levelname", "asctime", "module", "funcName", "lineno"]:
                self.colorize(record_copy, key)
            if "color_message" in record_copy.__dict__:
                record_copy.msg = record_copy.__dict__["color_message"]
                record_copy.__dict__["message"] = record_copy.getMessage()
        return super().formatMessage(record_copy)


class AccessFormatter(ColorFormatter):
    """
    A subclass of ``ColorFormatter`` specialized for logging uvicorn access logs.

    It adds a few custom fields as well as a coloring mechanism based on status code.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        color_fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Union[Literal["%"], Literal["{"], Literal["$"]] = "%",
        use_colors: Optional[bool] = None,
        colors: Optional[Dict[str, Dict[str, Any]]] = None,
        level_colors: Optional[Dict[int, Dict[str, Any]]] = None,
        status_code_colors: Optional[Dict[int, Dict[str, Any]]] = None,
    ):
        """
        Initializes the formatter. See ``ColorFormatter.init()`` for details.

        :param status_code_colors: A dictionary of status codes mapping to color
                                   specifiers. You can also use the special keys 1, 2,
                                   3, 4, and 5 to style all 100, 200, ... codes
                                   respectively.
        """
        super().__init__(
            fmt, color_fmt, datefmt, style, use_colors, colors, level_colors
        )
        self.status_code_colors = status_code_colors or {
            1: {"fg": "bright_white"},
            2: {"fg": "green"},
            3: {"fg": "yellow"},
            4: {"fg": "red"},
            5: {"fg": "bright_red"},
        }

    def _refine_color(
        self, record: logging.LogRecord, color: Dict[str, Any]
    ) -> Dict[str, Any]:
        color = super()._refine_color(record, color)
        if color.pop("status", False):
            status_code: int
            (_, _, _, _, status_code) = record.args  # type: ignore
            status_code_color = self.status_code_colors.get(status_code, None)
            if status_code_color is None:
                status_code_color = self.status_code_colors[status_code // 100]
            color = status_code_color | color
        return color

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        status_code: int
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = record_copy.args  # type: ignore
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ""
        setattr(record_copy, "client_addr", client_addr)
        setattr(record_copy, "method", method)
        setattr(record_copy, "full_path", full_path)
        setattr(record_copy, "http_version", http_version)
        setattr(record_copy, "status_code", status_code)
        setattr(record_copy, "status_phrase", status_phrase)

        if self.use_colors:
            for key in [
                "client_addr",
                "method",
                "full_path",
                "http_version",
                "status_code",
                "status_phrase",
            ]:
                self.colorize(record_copy, key)
        return super().formatMessage(record_copy)
