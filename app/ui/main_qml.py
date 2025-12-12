# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main():
    app = QGuiApplication(sys.argv)

    # Força estilo consistente
    import os
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    engine = QQmlApplicationEngine()

    # Caminho absoluto para main.qml
    qml_path = Path(__file__).resolve().parent / "qml" / "main.qml"

    if not qml_path.exists():
        raise FileNotFoundError(f"main.qml não encontrado em: {qml_path}")

    engine.load(qml_path.as_posix())

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
