"""Gerenciamento de configuração e identidade visual do CAPT Empresarial."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

from app.utils.logger import get_logger
from app.utils.paths import runtime_path, workspace_path

CONFIG_PATH = workspace_path("config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "empresa": "Grupo14D",
    "tema": "dark",
    "logo": "logo_empresa.png",
    "versao": "1.3.0",
    "build_id": "AUTO",
    "paleta": {
        "background": "#0f172a",
        "surface": "#182338",
        "accent": "#fbbf24",
        "texto": "#f8fafc",
        "borda": "#1e293b",
    },
    "rodape_texto": "Desenvolvido pelo Departamento de Tecnologia • Grupo14D",
}


class ConfigManager:
    """Carrega, valida e disponibiliza acesso ao config.json."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or CONFIG_PATH
        self._logger = get_logger("capt.config")
        self._data: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Recarrega a configuração a partir do disco."""
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            self._logger.warning("config.json ausente. Gerando arquivo padrão.")
            self._write(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)
        try:
            with open(self.path, "r", encoding="utf-8") as handler:
                payload = json.load(handler)
        except (OSError, json.JSONDecodeError) as exc:
            self._logger.error("Falha ao ler config.json: %s. Restaurando padrão.", exc)
            self._write(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)

        merged = dict(DEFAULT_CONFIG)
        merged.update(payload if isinstance(payload, dict) else {})
        if merged.get("build_id", "AUTO") in ("AUTO", "", None):
            merged["build_id"] = self._generate_build_id()
            self._logger.info("Novo build_id gerado automaticamente: %s", merged["build_id"])
            self._write(merged)
        return merged

    def _write(self, payload: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as handler:
            json.dump(payload, handler, indent=2, ensure_ascii=False)

    @staticmethod
    def _generate_build_id() -> str:
        return uuid.uuid4().hex[:8].upper()

    @property
    def data(self) -> Dict[str, Any]:
        """Retorna o dicionário bruto da configuração."""
        return dict(self._data)

    @property
    def company_name(self) -> str:
        return str(self._data.get("empresa", "Grupo14D"))

    @property
    def theme(self) -> str:
        return "light"

    @property
    def logo_path(self) -> Path:
        raw_logo = str(self._data.get("logo", "logo_empresa.png"))
        candidate = Path(raw_logo)
        if candidate.is_absolute():
            return candidate
        workspace_logo = workspace_path(raw_logo)
        if workspace_logo.exists():
            return workspace_logo
        return runtime_path(raw_logo)

    @property
    def version(self) -> str:
        return str(self._data.get("versao", "1.0.0"))

    @property
    def build_id(self) -> str:
        return str(self._data.get("build_id", "DESCONHECIDO"))

    @property
    def palette(self) -> Dict[str, str]:
        palette = self._data.get("paleta") or {}
        fallback = DEFAULT_CONFIG["paleta"]
        merged = dict(fallback)
        merged.update(palette if isinstance(palette, dict) else {})
        return merged

    @property
    def footer_text(self) -> str:
        return str(self._data.get("rodape_texto", DEFAULT_CONFIG["rodape_texto"]))


if __name__ == "__main__":
    raise SystemExit("O ConfigManager é usado apenas pelo aplicativo principal.")
