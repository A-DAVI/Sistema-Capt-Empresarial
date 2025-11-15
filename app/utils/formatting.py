# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime


def format_brl(valor: float) -> str:
    """Formata número em BRL: R$ 1.234,56"""
    try:
        return (
            f"R$ {valor:,.2f}"  # 1,234.56
            .replace(",", "X").replace(".", ",").replace("X", ".")  # 1.234,56
        )
    except Exception:
        return f"R$ {valor:.2f}".replace(".", ",")


def parse_float_brl(texto: str) -> float | None:
    try:
        if texto is None:
            return None
        s = str(texto).strip().replace(" ", "").replace("R$", "").replace(".", "").replace(",", ".")
        v = float(s)
        return v
    except Exception:
        return None


def validar_data(data_str: str) -> bool:
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_valor(valor_str: str) -> float | None:
    try:
        s = (valor_str or "").strip().replace(" ", "").replace("R$", "").replace(".", "").replace(",", ".")
        v = float(s)
        if v <= 0:
            return None
        return v
    except Exception:
        return None

