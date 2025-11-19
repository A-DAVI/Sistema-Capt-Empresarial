# -*- coding: utf-8 -*-
"""Utilidades para resolver caminhos em modo fonte e executável (PyInstaller)."""
from __future__ import annotations

from pathlib import Path
import sys


_SOURCE_ROOT = Path(__file__).resolve().parents[2]
_IS_FROZEN = bool(getattr(sys, "frozen", False))
_MEIPASS_ROOT = Path(getattr(sys, "_MEIPASS", _SOURCE_ROOT))
_EXEC_ROOT = Path(sys.executable).resolve().parent if _IS_FROZEN else _SOURCE_ROOT


def runtime_path(*parts: str | Path) -> Path:
    """Retorna caminhos para recursos empacotados (logo, temas, etc.)."""
    if not parts:
        return _MEIPASS_ROOT
    return _MEIPASS_ROOT.joinpath(*parts)


def workspace_path(*parts: str | Path) -> Path:
    """Retorna caminhos de trabalho/escrita (JSONs, logs, relatórios)."""
    if not parts:
        return _EXEC_ROOT
    return _EXEC_ROOT.joinpath(*parts)


def ensure_workspace_dir(*parts: str | Path) -> Path:
    """Garante que o diretório de trabalho solicitado exista."""
    destino = workspace_path(*parts)
    destino.mkdir(parents=True, exist_ok=True)
    return destino


__all__ = [
    "runtime_path",
    "workspace_path",
    "ensure_workspace_dir",
]
