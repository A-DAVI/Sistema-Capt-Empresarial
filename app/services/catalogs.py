# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable


def merge_categorias(base: Iterable[str], novas: Iterable[str]) -> list[str]:
    merged = {c.strip() for c in base if c.strip()}
    merged.update({c.strip() for c in novas if c.strip()})
    return sorted(merged, key=lambda v: v.lower())


def merge_fornecedores(base: Iterable[str], existentes: Iterable[str]) -> list[str]:
    merged = {f.strip().upper() for f in existentes if f.strip()}
    merged.update({f.strip().upper() for f in base if f.strip()})
    return sorted(merged, key=lambda v: v.lower())
