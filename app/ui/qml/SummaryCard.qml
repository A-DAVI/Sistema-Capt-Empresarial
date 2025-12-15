import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects

Rectangle {
    id: card

    //  ESSENCIAL PARA LAYOUTS
    implicitWidth: 220
    implicitHeight: 120

    radius: 12
    color: "#F7F9FC"
    border.color: "#E5E7EB"

    //  Shadow otimizado
    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 2
        radius: 10
        samples: 16
        color: "#18000000"
    }

    // API limpa
    property alias title: titleText.text
    property alias value: valueText.text
    property alias valueColor: valueText.color

    Column {
        anchors.centerIn: parent
        spacing: 6

        Text {
            id: titleText
            text: "Título"
            font.pixelSize: 12
            color: "#6B7280"
        }

        Text {
            id: valueText
            text: "Valor"
            font.pixelSize: 22
            font.weight: Font.Bold
            color: "#111827"
        }
    }
}

