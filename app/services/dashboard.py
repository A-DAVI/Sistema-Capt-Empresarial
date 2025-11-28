# -*- coding: utf-8 -*-
from __future__ import annotations

from collections import defaultdict, OrderedDict
from datetime import datetime
from typing import Iterable


def _parse_data(reg: dict) -> datetime | None:
    valor = reg.get("data") or ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, fmt)
        except Exception:
            continue
    return None


def agrupa_por_mes(despesas: Iterable[dict]) -> OrderedDict[str, float]:
    soma = defaultdict(float)
    for reg in despesas:
        dt = _parse_data(reg)
        if not dt:
            continue
        chave = dt.strftime("%Y-%m")
        try:
            soma[chave] += float(reg.get("valor", 0) or 0)
        except Exception:
            continue
    return OrderedDict(sorted(soma.items()))


def total_por_categoria(despesas: Iterable[dict], mes_ano: str | None = None) -> dict[str, float]:
    tot = defaultdict(float)
    for reg in despesas:
        dt = _parse_data(reg)
        if not dt:
            continue
        if mes_ano and dt.strftime("%Y-%m") != mes_ano:
            continue
        cat = str(reg.get("tipo") or reg.get("categoria") or "Sem categoria")
        try:
            tot[cat] += float(reg.get("valor", 0) or 0)
        except Exception:
            continue
    return dict(tot)


def calcular_kpis_por_idx(despesas: list[dict], idx: int, meses_disponiveis: list[str]) -> dict[str, str | bool]:
    agrupado = agrupa_por_mes(despesas)
    if not meses_disponiveis:
        return {
            "mes_atual_label": "—",
            "mes_anterior_label": "—",
            "total_mes_atual": "R$ 0,00",
            "total_mes_anterior": "R$ 0,00",
            "variacao": "+0.0%",
            "variacao_up": True,
            "maior_categoria": "N/A",
        }
    atual_key = meses_disponiveis[idx]
    prev_key = meses_disponiveis[idx - 1] if idx - 1 >= 0 else None
    atual_total = agrupado.get(atual_key, 0.0)
    prev_total = agrupado.get(prev_key, 0.0) if prev_key else 0.0
    variacao = 0.0
    if prev_total:
        variacao = ((atual_total - prev_total) / prev_total) * 100
    cats_mes = total_por_categoria(despesas, atual_key)
    maior_cat = max(cats_mes.items(), key=lambda x: x[1])[0] if cats_mes else "N/A"

    def fmt_mes(chave: str | None) -> str:
        if not chave:
            return "—"
        dt = datetime.strptime(chave, "%Y-%m")
        return dt.strftime("%b/%Y")

    def fmt_brl(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return {
        "mes_atual_label": fmt_mes(atual_key),
        "mes_anterior_label": fmt_mes(prev_key),
        "total_mes_atual": fmt_brl(atual_total),
        "total_mes_anterior": fmt_brl(prev_total),
        "variacao": f"{variacao:+.1f}%",
        "variacao_up": variacao >= 0,
        "maior_categoria": maior_cat,
    }


def dashboard_dto(despesas: list[dict], current_idx: int | None = None) -> dict:
    meses = list(agrupa_por_mes(despesas).keys())
    current_idx = len(meses) - 1 if current_idx is None else max(0, min(current_idx, len(meses) - 1))
    kpis = calcular_kpis_por_idx(despesas, current_idx, meses) if meses else calcular_kpis_por_idx(despesas, 0, [])
    mes_ref = meses[current_idx] if meses else None
    categorias = total_por_categoria(despesas, mes_ref) if mes_ref else total_por_categoria(despesas, None)
    return {
        "meses": meses,
        "mes_idx": current_idx,
        "kpis": kpis,
        "categorias": categorias,
    }
