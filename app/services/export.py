# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from app.utils.report import generate_pdf_report
from app.utils.paths import workspace_path


def export_pdf(registros: Iterable[dict], empresa_slug: str, company_label: str, logo_path: str | None = None) -> Path | None:
    registros = list(registros)
    if not registros:
        return None
    destino = workspace_path("relatorios")
    destino.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"relatorio_{empresa_slug}.pdf"
    caminho_destino = destino / nome_arquivo
    logo_param = logo_path if logo_path else None
    caminho = generate_pdf_report(registros, str(caminho_destino), company_name=company_label, logo_path=logo_param)
    return Path(caminho)


def export_csv(registros: Iterable[dict], empresa_slug: str) -> Path | None:
    registros = list(registros)
    if not registros:
        return None
    destino = workspace_path("relatorios")
    destino.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"relatorio_{empresa_slug}.csv"
    caminho_destino = destino / nome_arquivo
    with open(caminho_destino, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Data", "Tipo", "Forma", "Valor"])
        for gasto in registros:
            writer.writerow([
                gasto.get("data", ""),
                gasto.get("tipo", ""),
                gasto.get("forma_pagamento", ""),
                f"{float(gasto.get('valor', 0) or 0):.2f}".replace(".", ","),
            ])
    return caminho_destino
