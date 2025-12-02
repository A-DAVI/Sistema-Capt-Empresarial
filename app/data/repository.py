# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

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


class SQLiteDataRepository:
    """Repositório SQLite para despesas multiempresa (coluna empresa_id)."""

    def __init__(self, db_path: str | Path | None = None, empresa_id: str | None = None):
        self.path = Path(db_path) if db_path else workspace_path("gastos_empresas.sqlite")
        self.empresa_id = empresa_id or "empresa"
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _ensure_schema(self) -> None:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa_id TEXT,
                    data TEXT,
                    tipo TEXT,
                    forma_pagamento TEXT,
                    valor REAL,
                    fornecedor TEXT,
                    timestamp TEXT
                )
                """
            )
            conn.commit()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def load(self) -> list[dict[str, Any]]:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT data, tipo, forma_pagamento, valor, fornecedor, timestamp FROM despesas WHERE empresa_id = ?",
                (self.empresa_id,),
            )
            rows = cur.fetchall()
            result: list[dict[str, Any]] = []
            for data, tipo, forma, valor, fornecedor, ts in rows:
                result.append(
                    {
                        "data": data or "",
                        "tipo": tipo or "",
                        "forma_pagamento": forma or "",
                        "valor": float(valor or 0),
                        "fornecedor": fornecedor or "",
                        "timestamp": ts or "",
                    }
                )
            return result
        except Exception:
            return []
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def save(self, data: Iterable[dict[str, Any]]) -> None:
        registros = list(data)
        try:
            conn = self._connect()
            cur = conn.cursor()
            # remove registros da empresa atual antes de inserir
            cur.execute("DELETE FROM despesas WHERE empresa_id = ?", (self.empresa_id,))
            cur.executemany(
                """
                INSERT INTO despesas (empresa_id, data, tipo, forma_pagamento, valor, fornecedor, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        self.empresa_id,
                        reg.get("data", ""),
                        reg.get("tipo", ""),
                        reg.get("forma_pagamento", ""),
                        float(reg.get("valor", 0) or 0),
                        reg.get("fornecedor", ""),
                        reg.get("timestamp", ""),
                    )
                    for reg in registros
                ],
            )
            conn.commit()
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass


def get_repository(backend: str = "json", arquivo_dados: str | Path | None = None, empresa_id: str | None = None):
    """Factory simples para escolher backend. backend: 'json' (default) ou 'sqlite'."""
    backend = (backend or "json").lower()
    if backend == "sqlite":
        db_path = workspace_path("gastos_empresas.sqlite")
        return SQLiteDataRepository(db_path, empresa_id)
    return JsonDataRepository(arquivo_dados)
