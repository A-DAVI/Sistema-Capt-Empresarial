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


def montar_filtros_ui(data_inicio: str, data_fim: str, tipo: str, forma: str, fornecedor: str, valor: str) -> dict[str, str]:
    """Monta dict de filtros a partir dos campos da UI."""
    filtros = {}
    if data_inicio.strip():
        filtros["data_inicio"] = data_inicio.strip()
    if data_fim.strip():
        filtros["data_fim"] = data_fim.strip()
    if tipo and tipo != "Todos":
        filtros["tipo"] = tipo
    if forma and forma != "Todos":
        filtros["forma"] = forma
    if fornecedor and fornecedor != "Todos":
        filtros["fornecedor"] = fornecedor
    if valor and valor != "Todos":
        filtros["valor"] = valor
    return filtros


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


def montar_registro(
    data: str,
    tipo: str,
    forma_pagamento: str,
    valor_str: str,
    *,
    fornecedor: str | None = None,
    fornecedor_obrigatorio: bool = False,
    normalizar_categoria=None,
    normalizar_fornecedor=None,
) -> tuple[bool, str | dict]:
    """Valida e monta o dicionÃ¡rio de uma despesa."""
    ok, msg = validar_entrada(data, tipo, forma_pagamento, valor_str)
    if not ok:
        return False, msg

    if fornecedor_obrigatorio and not (fornecedor or "").strip():
        return False, "Fornecedor obrigatório para esta categoria."

    try:
        valor = validar_valor(valor_str)
    except Exception:
        valor = None
    if valor is None:
        return False, "Valor inválido! Digite um número maior que zero."

    tipo_final = normalizar_categoria(tipo) if normalizar_categoria else tipo
    fornecedor_final = normalizar_fornecedor(fornecedor) if normalizar_fornecedor else (fornecedor or None)

    registro = {
        "data": data,
        "tipo": tipo_final,
        "forma_pagamento": forma_pagamento,
        "valor": valor,
        "fornecedor": fornecedor_final or None,
        "timestamp": datetime.now().isoformat(),
    }
    return True, registro


def atualizar_registro(
    registros: list[dict[str, Any]],
    indice: int,
    *,
    data: str,
    tipo: str,
    forma_pagamento: str,
    valor_str: str,
    fornecedor: str | None,
    fornecedor_obrigatorio: bool,
    normalizar_categoria,
    normalizar_fornecedor,
) -> tuple[bool, str | list[dict[str, Any]]]:
    if indice < 0 or indice >= len(registros):
        return False, "Registro não encontrado."
    ok, resultado = montar_registro(
        data=data,
        tipo=tipo,
        forma_pagamento=forma_pagamento,
        valor_str=valor_str,
        fornecedor=fornecedor,
        fornecedor_obrigatorio=fornecedor_obrigatorio,
        normalizar_categoria=normalizar_categoria,
        normalizar_fornecedor=normalizar_fornecedor,
    )
    if not ok:
        return False, str(resultado)
    registros[indice] = resultado  # type: ignore[index]
    return True, registros


def remover_registro(registros: list[dict[str, Any]], indice: int) -> tuple[bool, str | list[dict[str, Any]]]:
    if indice < 0 or indice >= len(registros):
        return False, "Registro não encontrado."
    try:
        del registros[indice]
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return True, registros


# Helpers de formatação/validação para a UI
def formatar_valor_input(texto: str) -> str:
    """Formata string numérica em estilo brasileiro ##.###,##."""
    digits = "".join(ch for ch in texto if ch.isdigit())
    if not digits:
        return ""
    try:
        valor_centavos = int(digits)
    except Exception:
        return ""
    valor_float = valor_centavos / 100
    return (
        f"{valor_float:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data_input(texto: str) -> str:
    """Formata entrada de data para DD/MM/AAAA durante a digitação."""
    digits = "".join(ch for ch in texto if ch.isdigit())
    if not digits:
        return ""
    # limita a 8 dígitos
    digits = digits[:8]
    partes = []
    if len(digits) >= 2:
        partes.append(digits[:2])
    else:
        partes.append(digits)
        return "/".join(partes)
    if len(digits) >= 4:
        partes.append(digits[2:4])
    else:
        partes.append(digits[2:])
        return "/".join(partes)
    partes.append(digits[4:])
    return "/".join(partes)

