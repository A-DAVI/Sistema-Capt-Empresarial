# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config import DATA_DIR
from app.data.store import load_data, save_data


class JsonDataRepository:
    """Repositório simples baseado em arquivos JSON por empresa."""

    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir or DATA_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("app.data.repository")

    def resolve_company_file(self, company_ref: str | Path) -> Path:
        ref_path = Path(company_ref)
        if ref_path.suffix == "":
            ref_path = self.base_dir / f"{ref_path.name}.json"
        elif not ref_path.is_absolute():
            ref_path = self.base_dir / ref_path
        return ref_path

    def ensure_company_file(self, company_id: str) -> Path:
        arquivo = self.base_dir / f"{company_id}.json"
        if not arquivo.exists():
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text("[]", encoding="utf-8")
            self.logger.info("Arquivo criado para a empresa %s em %s", company_id, arquivo)
        return arquivo

    def load(self, company_ref: str | Path) -> list[dict[str, Any]]:
        arquivo = self.resolve_company_file(company_ref)
        return load_data(str(arquivo)) or []

    def save(self, company_ref: str | Path, dados: list[dict[str, Any]]) -> bool:
        arquivo = self.resolve_company_file(company_ref)
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        return save_data(str(arquivo), dados)

