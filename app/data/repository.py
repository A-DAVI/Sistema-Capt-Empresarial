# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.utils.paths import workspace_path


class JsonDataRepository:
    """Repositório simples baseado em JSON para despesas, categorias e fornecedores."""

    def __init__(self, arquivo_dados: str | Path | None = None):
        self.path = Path(arquivo_dados) if arquivo_dados else workspace_path("gastos_empresa.json")

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save(self, data: list[dict[str, Any]]) -> None:
        try:
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            # em produção deveríamos logar
            pass


def load_empresas_lista(base_dir: Path | None = None) -> list[Path]:
    """Lista arquivos de empresa em app/data (ou diretório informado)."""
    base = base_dir or workspace_path("app/data")
    if not base.exists():
        return []
    return sorted(p for p in base.glob("*.json") if p.is_file())
