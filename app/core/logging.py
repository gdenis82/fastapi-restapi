import logging
import re
from logging.config import dictConfig
from typing import Any, Mapping

from fastapi import Request

REDACTED_VALUE = "***"
SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "client_secret",
    "database_url",
    "password",
    "refresh_token",
    "secret",
    "token",
    "x_api_key",
}

_SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(api[_-]?key|authorization|password|secret|token|client_secret)\s*[=:]\s*[^,\s;]+"
)
_URL_PASSWORD_PATTERN = re.compile(r"(?i)://([^:/\s]+):([^@/\s]+)@")
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9\-._~+/]+=*")


def configure_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                }
            },
            "root": {
                "handlers": ["default"],
                "level": level,
            },
        }
    )


def sanitize_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return sanitize_mapping(value)
    if isinstance(value, (list, tuple)):
        return [sanitize_value(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def sanitize_mapping(mapping: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in mapping.items():
        normalized_key = normalize_key(key)
        if normalized_key in SENSITIVE_KEYS:
            sanitized[str(key)] = REDACTED_VALUE
        else:
            sanitized[str(key)] = sanitize_value(value)
    return sanitized


def normalize_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_")


def redact_text(text: str) -> str:
    text = _URL_PASSWORD_PATTERN.sub(r"://\1:***@", text)
    text = _BEARER_PATTERN.sub("Bearer ***", text)
    return _SENSITIVE_KEY_PATTERN.sub(r"\1=***", text)


def build_request_context(request: Request) -> dict[str, Any]:
    headers = sanitize_mapping(dict(request.headers))
    query_params = sanitize_mapping(dict(request.query_params))
    client_host = request.client.host if request.client else None
    return {
        "client": client_host,
        "headers": headers,
        "query": query_params,
    }
