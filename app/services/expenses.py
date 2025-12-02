# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from app.utils.formatting import format_brl, validar_data, validar_valor


def parse_data(data_str: str) -> datetime | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(data_str, fmt)
        except Exception:
            continue
    return None


def filtro_registros(registros: Iterable[dict[str, Any]], filtros: dict[str, str] | None) -> list[dict[str, Any]]:
    if not filtros:
        return list(registros)
    res = []
    data_ini = parse_data(filtros.get("data_inicio", "")) if filtros.get("data_inicio") else None
    data_fim = parse_data(filtros.get("data_fim", "")) if filtros.get("data_fim") else None
    tipo = filtros.get("tipo")
    forma = filtros.get("forma")
    for reg in registros:
        d = parse_data(reg.get("data", ""))
        if data_ini and (not d or d < data_ini):
            continue
        if data_fim and (not d or d > data_fim):
            continue
        if tipo and tipo != "Todos" and reg.get("tipo") != tipo:
            continue
        if forma and forma != "Todos" and reg.get("forma_pagamento") != forma:
            continue
        res.append(reg)
    return res


def normalizar_filtros(filtros: dict[str, str] | None) -> dict[str, Any]:
    """Normaliza filtros vindo da UI para uso nos serviÃ§os."""
    if not filtros:
        return {}
    normalizados: dict[str, Any] = {}
    data_inicio = parse_data(filtros.get("data_inicio", ""))
    data_fim = parse_data(filtros.get("data_fim", ""))
    if data_inicio:
        normalizados["data_inicio"] = data_inicio
    if data_fim:
        normalizados["data_fim"] = data_fim
    tipo = (filtros.get("tipo") or "").strip()
    if tipo and tipo.lower() not in ("todos", "selecionar", "selecione o tipo"):
        normalizados["tipo"] = tipo
    forma = (filtros.get("forma") or "").strip()
    if forma and forma != "Todos":
        normalizados["forma"] = forma
    fornecedor = (filtros.get("fornecedor") or "").strip()
    if fornecedor and fornecedor != "Todos":
        normalizados["fornecedor"] = fornecedor
    valor = (filtros.get("valor") or "").strip()
    if valor and valor != "Todos":
        normalizados["valor"] = valor
    return normalizados


def filtro_com_faixa(registros: Iterable[dict[str, Any]], filtros: dict[str, str] | None) -> list[dict[str, Any]]:
    """Aplica filtros básicos + faixa de valor."""
    filtros_norm = normalizar_filtros(filtros)
    if not filtros_norm:
        return list(registros)

    # separa valor
    faixa_valor = filtros_norm.pop("valor", None)
    base = filtro_registros(registros, filtros_norm)

    def corresponde_valor(valor: float, criterio: str | None) -> bool:
        if not criterio or criterio == "Todos":
            return True
        if criterio == "Até 100":
            return valor <= 100
        if criterio == "100 a 500":
            return 100 < valor <= 500
        if criterio == "500 a 1000":
            return 500 < valor <= 1000
        if criterio == "Acima de 1000":
            return valor > 1000
        return True

    resultado = []
    for reg in base:
        try:
            v = float(reg.get("valor", 0) or 0)
        except Exception:
            v = 0
        if not corresponde_valor(v, faixa_valor):
            continue
        resultado.append(reg)
    return resultado


def resumo_kpis(registros: Iterable[dict[str, Any]]) -> dict[str, str]:
    total = 0.0
    qtd = 0
    for r in registros:
        try:
            total += float(r.get("valor", 0) or 0)
            qtd += 1
        except Exception:
            continue
    return {
        "total_str": format_brl(total),
        "quantidade_str": f"{qtd} registros" if qtd != 1 else "1 registro",
        "total": total,
        "quantidade": qtd,
    }


def validar_entrada(data: str, tipo: str, forma: str, valor: str) -> tuple[bool, str]:
    if not validar_data(data):
        return False, "Data invÃ¡lida. Use o formato DD/MM/AAAA."
    if not tipo or tipo == "Selecione o tipo":
        return False, "Selecione um tipo de despesa."
    if not forma or forma == "Selecione a forma":
        return False, "Selecione a forma de pagamento."
    if not validar_valor(valor):
        return False, "Valor invÃ¡lido! Digite um nÃºmero maior que zero."
    return True, ""

