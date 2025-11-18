# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent

DATA_DIR = APP_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "relatorios"
LOG_DIR = PROJECT_ROOT / "logs"

LOGO_PATH = PROJECT_ROOT / "logo_empresa.png"
LOGO_ICON_CANDIDATES = ["logo_icon.ico", "logo_icon.png", "logo_icon.gif"]

EMPRESAS_PRE_CONFIGURADAS = [
    {"id": "empresa_1", "nome": "Empresa 01"},
    {"id": "empresa_2", "nome": "Empresa 02"},
    {"id": "empresa_3", "nome": "Empresa 03"},
]

BRAND_COLORS = {
    "background": "#0B0B0B",
    "surface": "#121212",
    "panel": "#1A1A1A",
    "accent": "#007BFF",
    "accent_hover": "#0056B3",
    "neutral": "#1F1F1F",
    "text_primary": "#FFFFFF",
    "text_secondary": "#CCCCCC",
    "text_muted": "#8A8A8A",
    "success": "#1ABC9C",
    "danger": "#C0392B",
}

FONT_FAMILY = "Segoe UI"

