import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: root
    height: 44

    model: [
        "Empresa Exemplo LTDA",
        "Cliente ABC",
        "Grupo 14D"
    ]

    currentIndex: -1
    displayText: currentIndex === -1 ? "Selecione a empresa" : currentText

    background: Rectangle {
        radius: 8
        border.color: "#CBD5E1"
        color: "white"
    }

    contentItem: Text {
        text: root.displayText
        color: "#0F172A"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 12
    }
}
