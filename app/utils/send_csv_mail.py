# -*- coding: utf-8 -*-
"""
Envio de CSV por e-mail a partir da pasta 'entrada'.

Uso esperado:
    1) Coloque o CSV exportado em ./entrada (ex.: "CSV - GRUPO14D - empresa.csv").
    2) Execute:  python app/utils/send_csv_mail.py  [--arquivo caminho/do/csv]
       - Se não informar --arquivo, o script pega o CSV mais recente em ./entrada.

Configuração de SMTP via variáveis de ambiente:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_TO
    (SMTP_TO pode ser separado por vírgulas)

O script não depende da UI; é apenas um auxiliar para o cliente receber o CSV por e-mail.
"""
from __future__ import annotations

import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[2]
ENTRADA_DIR = BASE_DIR / "entrada"


def _carregar_smtp() -> dict[str, str]:
    """Lê as credenciais do ambiente (e .env, se disponível)."""
    # carrega .env na raiz, se houver
    if load_dotenv:
        load_dotenv(BASE_DIR / ".env")
    cfg = {
        "host": os.getenv("SMTP_HOST", ""),
        "port": os.getenv("SMTP_PORT", "587"),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from": os.getenv("SMTP_FROM", ""),
        "to": os.getenv("SMTP_TO", ""),
    }
    if not all([cfg["host"], cfg["port"], cfg["from"], cfg["to"]]):
        raise RuntimeError(
            "Configure SMTP_HOST, SMTP_PORT, SMTP_FROM e SMTP_TO no ambiente para envio de e-mail."
        )
    return cfg


def _encontrar_csv(arquivo_arg: str | None) -> Path:
    """Retorna o arquivo CSV informado ou o mais recente na pasta ./entrada."""
    if arquivo_arg:
        p = Path(arquivo_arg)
        if not p.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado: {p}")
        return p

    ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
    csvs = sorted(ENTRADA_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csvs:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {ENTRADA_DIR}")
    return csvs[0]


def _criar_email(cfg: dict[str, str], arquivo: Path, empresa: str | None = None) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"CSV - GRUPO14D ({arquivo.name})"
    msg["From"] = cfg["from"]
    msg["To"] = ", ".join([t.strip() for t in cfg["to"].split(",") if t.strip()])
    empresa_hint = empresa or cfg.get("empresa_hint", "<EMPRESA>")
    msg.set_content(
        f"Olá!\n\n"
        f"Detectamos que um relatório da {empresa_hint} foi exportado pelo Sistema.\n"
        "Segue em anexo o relatório. Qualquer dúvida, entre em contato com o setor de tecnologia.\n\n"
        "Equipe Grupo 14D"
    )

    data = arquivo.read_bytes()
    msg.add_attachment(
        data,
        maintype="text",
        subtype="csv",
        filename=arquivo.name,
    )
    return msg


def enviar_csv(arquivo: Path, empresa: str | None = None) -> None:
    cfg = _carregar_smtp()
    msg = _criar_email(cfg, arquivo, empresa)
    port = int(cfg["port"])
    with smtplib.SMTP(cfg["host"], port) as server:
        server.starttls()
        if cfg["user"] and cfg["password"]:
            server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
    print(f"E-mail enviado com {arquivo.name} para {cfg['to']}")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Enviar CSV da pasta entrada via e-mail.")
    parser.add_argument("--arquivo", help="Caminho de um CSV específico (opcional).")
    parser.add_argument("--empresa", help="Nome da empresa (opcional, para o corpo do e-mail).")
    args = parser.parse_args(list(argv) if argv is not None else None)

    alvo = _encontrar_csv(args.arquivo)
    enviar_csv(alvo, empresa=args.empresa)


if __name__ == "__main__":
    main()
