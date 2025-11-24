
"""Logger utilitário com rotação automática para o CAPT Empresarial."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from typing import Dict

from app.utils.paths import workspace_path

LOG_DIR = workspace_path("logs")
LOG_FILE = LOG_DIR / "app.log"
_MAX_BYTES = 512 * 1024
_BACKUP_COUNT = 5

_LOGGER_CACHE: Dict[str, logging.Logger] = {}


def _prepare_directory() -> None:
    """Garante que o diretório de logs exista antes de anexar handlers."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str = "capt") -> logging.Logger:
    """Retorna um logger com rotação configurada e cacheado por nome."""
    cached = _LOGGER_CACHE.get(name)
    if cached:
        return cached

    _prepare_directory()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    _LOGGER_CACHE[name] = logger
    return logger


def log_exception(exc: BaseException, context: str | None = None) -> None:
    """Registra uma exceção crítica com contexto opcional."""
    logger = get_logger("capt.exception")
    ctx = f" ({context})" if context else ""
    logger.exception("Falha inesperada%s: %s", ctx, exc)


if __name__ == "__main__":  # Protege contra execução direta acidental.
    raise SystemExit("Modulo utilitário; execute o app principal para usá-lo.")
