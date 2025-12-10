# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable, Callable, Any


def merge_categorias(base: Iterable[str], novas: Iterable[str]) -> list[str]:
    merged = {c.strip() for c in base if c.strip()}
    merged.update({c.strip() for c in novas if c.strip()})
    return sorted(merged, key=lambda v: v.lower())


def merge_fornecedores(base: Iterable[str], existentes: Iterable[str]) -> list[str]:
    merged = {f.strip().upper() for f in existentes if f.strip()}
    merged.update({f.strip().upper() for f in base if f.strip()})
    return sorted(merged, key=lambda v: v.lower())


# Bases padrão para categorias, fornecedores e formas de pagamento
CATEGORIAS_FLAGS_BASE: list[tuple[str, bool]] = [
    ("Água e esgoto", False),
    ("Energia Elétrica", False),
    ("Telefone", False),
    ("Correios e Malotes", False),
    ("FGTS", False),
    ("DARF INSS", False),
    ("ICMS", False),
    ("Impostos Fiscais (PIS, Cofins, IRP e CSLL)", False),
    ("Simples Nacional", False),
    ("Salários (Funcionários)", False),
    ("Férias (Funcionários)", False),
    ("Rescisão (Funcionários)", False),
    ("13º Salário (Funcionários)", False),
    ("Pro-labore (Sócios)", False),
    ("Aluguel", False),
    ("Tarifas bancarias", False),
    ("Combustível lubrificante", True),
    ("Serviços de terceiros", True),
    ("Internet", False),
    ("Fretes e transportes", True),
    ("Materiais de consumo", True),
    ("Comissão de venda", True),
    ("Despesa de viagem", False),
    ("Fornecedores de matéria prima, embalagens e insumos", True),
    ("Honorários", False),
    ("Consultoria jurídica", True),
    ("Manutenção de equipamentos", True),
    ("Bens de pequeno valor", True),
    ("Imobilizado - Veículo", True),
    ("Imobilizado - Máquina e equipamentos", True),
    ("Imobilizado - Computadores e Periféricos", True),
    ("Manutenção de veículos", True),
    ("Alvará e taxa de licença sanitária", False),
    ("IPVA e licenciamento", False),
    ("IPTU", False),
]

FORNECEDORES_BASE: list[str] = [
    "PMAN SERVICOS REPRESENTACOES COM E IND LTDA",
    "COLMEIA DISTRIBUIDORA LTDA",
    "SOLUCAO, INGREDIENTES INDUSTRIAIS LTDA",
    "KASSIA FLORES LTDA",
    "ETIQUETAS MARINGA LTDA",
    "SANTA ROSA COMERCIO DE EMBALAGENS LTDA-EPP",
    "COMERCIO DE CHAPAS DE MDF LAMINIL LTDA",
    "CLEVERSON GERALDO RODRIGUES - ME",
    "ALMEVAN DISTRIBUIDORA DE ALIMENTOS LTDA",
    "BEBIDAS WHITE RIVER LTDA",
    "USINA ALTO ALEGRE S.A - ACUCAR E ALCOOL",
    "PALUMA VARIEDADES LTDA",
    "SUNNYVALE COM E REPRES LTDA",
    "CELERITAS DISTRIBUICAO DE BEBIDAS EM GERAL LTDA",
    "IND. COM. BEBIDAS FUNADA LTDA",
    "L DUARTE ALVES LTDA",
    "DIFRIPAR LOGISTICA E DISTRIBUICAO LTDA",
    "COFERPAN - COM FERM E PROD PANIF LTDA",
    "ARILU DISTRIBUIDORA S/A",
    "OESA COMERCIO E REPRESENTACOES S/A",
    "DISTRIBUIDORA DE GEN ALIM COLUMBIA LTDA",
    "TRANS APUCARANA TRANSPORTES RODOVIARIOS LTDA",
    "RODOVIARIO AFONSO LTDA",
    "ATACADAO S.A.",
    "SUPERMERCADO GUGUY LTDA",
    "M.J. DISTRIBUIDORA",
    "BAKER FAF LTDA",
    "COAGRU COOPERATIVA AGROINDUSTRIAL UNIAO",
]

FORMAS_BASE: list[str] = [
    "Banco 1",
    "Banco 2",
    "Banco 3",
    "Banco 4",
    "Banco 5",
    "Dinheiro",
]


def build_catalogs(
    existentes_categorias: Iterable[str] | None = None,
    existentes_fornecedores: Iterable[str] | None = None,
    normalizar_categoria: Callable[[str], Any] | None = None,
    normalizar_fornecedor: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    """Monta catálogos consolidados (categorias, fornecedores, formas)."""
    norm_cat = normalizar_categoria or (lambda x: x)
    norm_forn = normalizar_fornecedor or (lambda x: x)

    # categorias
    cats_base_norm = [(norm_cat(nome), precisa) for nome, precisa in CATEGORIAS_FLAGS_BASE]
    existentes_norm = []
    if existentes_categorias:
        existentes_norm = [(norm_cat(nome), False) for nome in existentes_categorias if nome]
    cats_merged = {nome: precisa for nome, precisa in cats_base_norm}
    for nome, precisa in existentes_norm:
        if not nome:
            continue
        cats_merged[nome] = cats_merged.get(nome, False) or bool(precisa)
    categorias_requer = {n for n, p in cats_merged.items() if p}
    categorias = sorted(cats_merged.keys(), key=lambda v: str(v).lower())

    # fornecedores
    fornecedores = merge_fornecedores(FORNECEDORES_BASE, existentes_fornecedores or [])
    fornecedores = [norm_forn(f) for f in fornecedores if f]

    # formas
    formas = FORMAS_BASE.copy()

    return {
        "categorias": categorias,
        "categorias_requer_fornecedor": categorias_requer,
        "fornecedores": fornecedores,
        "formas": formas,
    }


def categoria_exige_fornecedor(categorias_requer: set[str], categoria: str, normalizar_categoria=None) -> bool:
    norm = normalizar_categoria or (lambda x: x)
    cat_norm = norm(categoria)
    return cat_norm in categorias_requer


def add_categoria(categorias: list[str], nova: str, normalizar_categoria=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_categoria or (lambda x: x.strip())
    nova_norm = norm(nova)
    if not nova_norm:
        return False, "Informe o nome da categoria."
    if any(nova_norm.lower() == c.lower() for c in categorias):
        return False, "Categoria já existe."
    categorias.append(nova_norm)
    return True, sorted(categorias, key=lambda v: v.lower())


def renomear_categoria(categorias: list[str], atual: str, novo: str, normalizar_categoria=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_categoria or (lambda x: x.strip())
    atual_norm = norm(atual)
    novo_norm = norm(novo)
    if not atual_norm:
        return False, "Selecione uma categoria."
    if not novo_norm:
        return False, "Informe o novo nome."
    if any(novo_norm.lower() == c.lower() for c in categorias if c.lower() != atual_norm.lower()):
        return False, "Já existe uma categoria com esse nome."
    for i, c in enumerate(categorias):
        if c.lower() == atual_norm.lower():
            categorias[i] = novo_norm
            break
    return True, sorted(categorias, key=lambda v: v.lower())


def remover_categoria(categorias: list[str], alvo: str, normalizar_categoria=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_categoria or (lambda x: x.strip())
    alvo_norm = norm(alvo)
    if not alvo_norm:
        return False, "Selecione uma categoria."
    categorias = [c for c in categorias if c.lower() != alvo_norm.lower()]
    return True, sorted(categorias, key=lambda v: v.lower())


def add_fornecedor(lista: list[str], novo: str, normalizar_fornecedor=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_fornecedor or (lambda x: x.strip().upper())
    novo_norm = norm(novo)
    if not novo_norm:
        return False, "Informe o nome do fornecedor."
    if any(novo_norm.lower() == f.lower() for f in lista):
        return False, "Fornecedor já existe."
    lista.append(novo_norm)
    return True, sorted(lista, key=lambda v: v.lower())


def renomear_fornecedor(lista: list[str], atual: str, novo: str, normalizar_fornecedor=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_fornecedor or (lambda x: x.strip().upper())
    atual_norm = norm(atual)
    novo_norm = norm(novo)
    if not atual_norm:
        return False, "Selecione um fornecedor."
    if not novo_norm:
        return False, "Informe o novo nome."
    if any(novo_norm.lower() == f.lower() for f in lista if f.lower() != atual_norm.lower()):
        return False, "Já existe um fornecedor com esse nome."
    for i, f in enumerate(lista):
        if f.lower() == atual_norm.lower():
            lista[i] = novo_norm
            break
    return True, sorted(lista, key=lambda v: v.lower())


def remover_fornecedor(lista: list[str], alvo: str, normalizar_fornecedor=None) -> tuple[bool, str | list[str]]:
    norm = normalizar_fornecedor or (lambda x: x.strip().upper())
    alvo_norm = norm(alvo)
    if not alvo_norm:
        return False, "Selecione um fornecedor."
    lista = [f for f in lista if f.lower() != alvo_norm.lower()]
    return True, sorted(lista, key=lambda v: v.lower())
