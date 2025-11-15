# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any


def _mock_gastos() -> list[dict[str, Any]]:
    """Mock de dados para ambiente de desenvolvimento."""
    hoje = datetime.now()
    base = hoje.replace(hour=0, minute=0, second=0, microsecond=0)

    def d(offset: int) -> str:
        return (base - timedelta(days=offset)).strftime("%d/%m/%Y")

    return [
        {
            "data": d(0),
            "tipo": "Salários e Encargos",
            "forma_pagamento": "Transferência Bancária",
            "valor": 18500.00,
            "timestamp": hoje.isoformat(),
        },
        {
            "data": d(1),
            "tipo": "Aluguel",
            "forma_pagamento": "PIX",
            "valor": 8200.00,
            "timestamp": (base - timedelta(days=1, hours=2)).isoformat(),
        },
        {
            "data": d(2),
            "tipo": "Energia Elétrica",
            "forma_pagamento": "Boleto",
            "valor": 1450.75,
            "timestamp": (base - timedelta(days=2, hours=1)).isoformat(),
        },
        {
            "data": d(3),
            "tipo": "Internet/Telefone",
            "forma_pagamento": "Cartão de Crédito",
            "valor": 650.40,
            "timestamp": (base - timedelta(days=3, hours=3)).isoformat(),
        },
        {
            "data": d(4),
            "tipo": "Combustível",
            "forma_pagamento": "Cartão de Débito",
            "valor": 980.00,
            "timestamp": (base - timedelta(days=4, hours=4)).isoformat(),
        },
        {
            "data": d(5),
            "tipo": "Marketing",
            "forma_pagamento": "Cartão de Crédito",
            "valor": 3200.00,
            "timestamp": (base - timedelta(days=5, hours=1)).isoformat(),
        },
        {
            "data": d(6),
            "tipo": "Software/Licenças",
            "forma_pagamento": "Cartão de Crédito",
            "valor": 1250.00,
            "timestamp": (base - timedelta(days=6, hours=2)).isoformat(),
        },
        {
            "data": d(7),
            "tipo": "Outros",
            "forma_pagamento": "Dinheiro",
            "valor": 430.00,
            "timestamp": (base - timedelta(days=7, hours=5)).isoformat(),
        },
    ]


def load_data(path: str) -> list[dict[str, Any]]:
    """Carrega os dados do JSON; em ambiente de dev sempre usa mock."""
    if os.getenv("APP_ENV", "").lower() == "dev":
        return _mock_gastos()

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_data(path: str, data: list[dict[str, Any]]) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

