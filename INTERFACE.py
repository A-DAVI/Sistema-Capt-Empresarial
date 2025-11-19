import sys
from pathlib import Path

def _prepare_sys_path() -> None:
    """Inclui o diretório raiz somente em modo desenvolvimento."""
    if getattr(sys, "frozen", False):
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parent

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

_prepare_sys_path()

# Importa o updater antes de importar o app
from app.utils.updater import auto_update

from app.ui.app import main


if __name__ == "__main__":
    # Executa o updater APENAS se estiver rodando como EXE
    if getattr(sys, "frozen", False):
        print("Modo EXE detectado: iniciando auto_update")
        auto_update()
    else:
        print("Modo script detectado: pulando auto_update")

    main()
