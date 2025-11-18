# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


def parse_data_str(valor: str | None) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%d/%m/%Y")
    except (ValueError, TypeError):
        return None


def normalizar_filtros(filtros: dict[str, str] | None) -> dict[str, Any]:
    if not filtros:
        return {}

    normalizados: dict[str, Any] = {}
    data_inicio = parse_data_str(filtros.get("data_inicio"))
    data_fim = parse_data_str(filtros.get("data_fim"))
    if data_inicio:
        normalizados["data_inicio"] = data_inicio
    if data_fim:
        normalizados["data_fim"] = data_fim

    tipo = (filtros.get("tipo") or "").strip()
    if tipo and tipo != "Todos":
        normalizados["tipo"] = tipo

    forma = (filtros.get("forma") or "").strip()
    if forma and forma != "Todos":
        normalizados["forma"] = forma

    return normalizados


def registro_atende_filtros(gasto: dict[str, Any], filtros: dict[str, Any]) -> bool:
    if not filtros:
        return True

    data_gasto = parse_data_str(str(gasto.get("data", "")))
    data_inicio = filtros.get("data_inicio")
    data_fim = filtros.get("data_fim")
    if data_inicio and (not data_gasto or data_gasto < data_inicio):
        return False
    if data_fim and (not data_gasto or data_gasto > data_fim):
        return False

    tipo = filtros.get("tipo")
    if tipo and gasto.get("tipo") != tipo:
        return False

    forma = filtros.get("forma")
    if forma and gasto.get("forma_pagamento") != forma:
        return False

    return True


def filtrar_registros(registros: Iterable[dict[str, Any]], filtros: dict[str, str] | None) -> list[dict[str, Any]]:
    filtros_norm = normalizar_filtros(filtros)
    if not filtros_norm:
        return list(registros)

    return [reg for reg in registros if registro_atende_filtros(reg, filtros_norm)]


def calcular_resumo(registros: Iterable[dict[str, Any]]) -> tuple[float, int]:
    registros_list = list(registros)
    total = sum(float((g.get("valor") or 0)) for g in registros_list)
    quantidade = len(registros_list)
    return total, quantidade

