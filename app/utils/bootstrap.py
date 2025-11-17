"""Inicialização segura do CAPT Empresarial."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.data import store
from app.utils.config import ConfigManager
from app.utils.logger import get_logger
from app.utils.security import (
    InstanceLock,
    ensure_json_integrity,
    install_global_exception_hook,
    validate_environment,
)

LOGGER = get_logger("capt.bootstrap")


@dataclass
class BootstrapContext:
    """Dados compartilhados após a inicialização segura."""

    config: ConfigManager
    data_path: Path
    instance_lock: InstanceLock


def _show_message(title: str, message: str) -> None:
    """Exibe mensagem amigável mesmo antes da UI principal."""
    try:
        from tkinter import Tk, messagebox

        root = Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:  # noqa: BLE001
        print(f"{title}: {message}")


def _default_data_factory():
    return store.get_default_data()


def bootstrap_application(data_file: Path | None = None) -> BootstrapContext:
    """Executa todas as verificações antes de criar a UI."""
    LOGGER.info("Inicializando camada de segurança.")
    validate_environment([Path("dist"), Path("build")])

    config = ConfigManager()
    data_target = data_file or Path("gastos_empresa.json")
    ensure_json_integrity(data_target, _default_data_factory)

    lock = InstanceLock("capt_empresarial")
    if not lock.acquire():
        _show_message(
            "Instância em execução",
            "O CAPT Empresarial já está em execução. Feche a instância atual antes de abrir novamente.",
        )
        raise SystemExit(2)

    def _notify(exc: BaseException) -> None:
        _show_message(
            "Erro crítico",
            f"Ocorreu um erro inesperado e foi registrado em logs/app.log.\n\nDetalhes: {exc}",
        )

    install_global_exception_hook(_notify)
    LOGGER.info("Bootstrap concluído. Versão %s (%s)", config.version, config.build_id)

    return BootstrapContext(config=config, data_path=data_target, instance_lock=lock)


if __name__ == "__main__":
    raise SystemExit("Bootstrap não deve ser executado diretamente.")
