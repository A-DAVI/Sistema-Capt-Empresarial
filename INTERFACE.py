# -*- coding: utf-8 -*-
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

from app.ui.app import main
from app.utils.updater import auto_update


if __name__ == "__main__":
    auto_update()
    main()
