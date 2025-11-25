"""Rotinas de segurança, integridade e inicialização do CAPT Empresarial."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, List, Sequence

try:
    import msvcrt  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    msvcrt = None

try:
    import fcntl  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    fcntl = None

from app.utils.logger import get_logger
from app.utils.paths import workspace_path

logger = get_logger("capt.security")

_CHECKSUM_SUFFIX = ".sha256"
_BACKUP_SUFFIX = ".bak"
_CRITICAL_FOLDERS: Sequence[Path] = (
    workspace_path("app", "data"),
    workspace_path("relatorios"),
    workspace_path("logs"),
)


def _checksum_path(target: Path) -> Path:
    return target.with_suffix(target.suffix + _CHECKSUM_SUFFIX)


def validate_environment(extra_paths: Iterable[Path] | None = None) -> List[Path]:
    """Cria pastas críticas e retorna a lista das que foram tocadas."""
    touched: List[Path] = []
    for folder in list(_CRITICAL_FOLDERS) + list(extra_paths or []):
        folder.mkdir(parents=True, exist_ok=True)
        touched.append(folder)
    return touched


def calculate_checksum(file_path: Path) -> str:
    """Calcula o hash SHA256 de um arquivo arbitrário."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as handler:
        while chunk := handler.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def persist_checksum(file_path: Path, checksum: str | None = None) -> str:
    """Salva o checksum em arquivo auxiliar."""
    checksum = checksum or calculate_checksum(file_path)
    with open(_checksum_path(file_path), "w", encoding="utf-8") as handler:
        handler.write(checksum)
    return checksum


def checksum_is_valid(file_path: Path) -> bool:
    """Confere se o checksum salvo combina com o arquivo alvo."""
    marker = _checksum_path(file_path)
    if not marker.exists() or not file_path.exists():
        return False
    current = calculate_checksum(file_path)
    try:
        saved = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return saved == current


def _write_json(target: Path, payload: Any) -> None:
    with open(target, "w", encoding="utf-8") as handler:
        json.dump(payload, handler, indent=2, ensure_ascii=False)


def ensure_json_integrity(file_path: Path, data_factory: Callable[[], Any]) -> bool:
    """Valida o JSON informado e restaura via factory quando necessário."""
    if not file_path.exists():
        payload = data_factory()
        _write_json(file_path, payload)
        persist_checksum(file_path)
        return True

    if not checksum_is_valid(file_path):
        logger.warning("Checksum inválido para %s. Executando restauração.", file_path)
        return restore_json_file(file_path, data_factory)

    try:
        with open(file_path, "r", encoding="utf-8") as handler:
            json.load(handler)
        return True
    except (OSError, json.JSONDecodeError):
        logger.error("JSON corrompido em %s. Restaurando backup.", file_path)
        return restore_json_file(file_path, data_factory)


def restore_json_file(file_path: Path, data_factory: Callable[[], Any]) -> bool:
    """Recria o arquivo JSON com dados padrões."""
    try:
        payload = data_factory()
        _write_json(file_path, payload)
        backup_path = file_path.with_suffix(file_path.suffix + _BACKUP_SUFFIX)
        backup_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        persist_checksum(file_path)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("Falha ao restaurar %s: %s", file_path, exc)
    return False


class InstanceLock:
    """Realiza locking via arquivo para impedir múltiplas instâncias."""

    def __init__(self, name: str = "capt_app") -> None:
        safe_name = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_"))
        self._lock_file = Path(tempfile.gettempdir()) / f"{safe_name}.lock"
        self._handle = None

    def acquire(self) -> bool:
        """Tenta adquirir o lock, retornando True em caso de sucesso."""
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        handle = open(self._lock_file, "a+")
        try:
            if os.name == "nt" and msvcrt:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            elif fcntl:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
            else:
                raise RuntimeError("Plataforma sem suporte de lock refinado.")
            handle.seek(0)
            handle.truncate()
            handle.write(str(os.getpid()))
            handle.flush()
            self._handle = handle
            return True
        except (OSError, RuntimeError):
            handle.close()
            return False

    def release(self) -> None:
     """Libera o lock caso ele esteja ativo."""
     if not self._handle:
        return
    
     try:
        if os.name == "nt" and msvcrt:
            try:
                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            except PermissionError:
                pass  # <<< IGNORA ERRO DE PERMISSÃO
        elif fcntl:
            try:
                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass  # <<< IGNORA ERRO
     finally:
        try:
            self._handle.close()
        except:
            pass
        self._handle = None

def install_global_exception_hook(
    notify_user: Callable[[BaseException], None] | None = None,
) -> None:
    """Instala um hook global em sys.excepthook para registrar falhas críticas."""

    def _hook(exc_type, exc, tb):  # noqa: ANN001
        logger.exception("Exceção não tratada", exc_info=(exc_type, exc, tb))
        if notify_user and exc:
            try:
                notify_user(exc)
            except Exception:  # noqa: BLE001
                pass

    sys.excepthook = _hook


if __name__ == "__main__":
    raise SystemExit("Execute apenas via módulo principal.")
