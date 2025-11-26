import sys
from pathlib import Path


def _prepare_sys_path() -> None:
    """Inclui o diretorio raiz apenas em modo desenvolvimento."""
    if getattr(sys, "frozen", False):
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parent

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_prepare_sys_path()

from app.ui.app import main
from app.utils.bootstrap import bootstrap_application
from app.bootstrap.updater import auto_update


if __name__ == "__main__":
    # Executa auto-update apenas no binario empacotado
    if getattr(sys, "frozen", False):
        try:
            auto_update()
        except Exception:
            pass

    # Inicializa bootstrap e lock para evitar multiplas instancias
    bootstrap_ctx = bootstrap_application()
    try:
        main(theme_mode=bootstrap_ctx.config.theme, config_path=str(bootstrap_ctx.config.path))
    finally:
        # Libera o lock ao sair
        bootstrap_ctx.instance_lock.release()
