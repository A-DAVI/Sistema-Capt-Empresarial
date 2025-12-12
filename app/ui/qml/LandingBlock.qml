import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: parent.width

    implicitHeight: Math.max(
        textLeft.implicitHeight,
        textRight.implicitHeight,
        visualBox.height
    ) + 80

    // ─── TEXTO ───
    property string title: ""
    property string subtitle: ""
    property string text: ""
    property var listItems: []
    property bool alignRight: false

    // ─── ILUSTRAÇÃO ───
    property url illustrationSource: ""
    property real imageScale: 1.0   // 👈 CONTROLE POR BLOCO

    Row {
        width: parent.width
        spacing: 80
        // ❌ SEM anchors aqui

        // ─── TEXTO ESQUERDA ───
        Column {
            id: textLeft
            width: parent.width * 0.45
            spacing: 12
            visible: !alignRight

            Text {
                text: title
                width: parent.width
                font.pixelSize: 28
                font.bold: true
                color: "#0F172A"
                wrapMode: Text.WordWrap
            }

            Text {
                text: subtitle
                width: parent.width
                font.pixelSize: 17
                color: "#475569"
                visible: subtitle !== ""
                wrapMode: Text.WordWrap
            }

            Text {
                text: root.text
                width: parent.width
                font.pixelSize: 15
                color: "#64748B"
                visible: root.text !== ""
                wrapMode: Text.WordWrap
            }

            Column {
                width: parent.width
                spacing: 6
                visible: listItems.length > 0

                Repeater {
                    model: listItems
                    Text {
                        text: "•  " + modelData
                        width: parent.width
                        font.pixelSize: 15
                        color: "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // ─── ILUSTRAÇÃO ───
        Item {
            id: visualBox
            width: 420
            height: 320   // 👈 PADRÃO BASE

            Image {
                anchors.centerIn: parent
                source: illustrationSource
                fillMode: Image.PreserveAspectFit
                smooth: true
                visible: illustrationSource !== ""

                width: parent.width * imageScale
                height: parent.height * imageScale
            }

            // fallback
            Text {
                anchors.centerIn: parent
                text: "14D"
                font.pixelSize: 88
                font.bold: true
                color: "#0D6EFD"
                opacity: illustrationSource === "" ? 0.06 : 0
            }
        }

        // ─── TEXTO DIREITA ───
        Column {
            id: textRight
            width: parent.width * 0.45
            spacing: 12
            visible: alignRight

            Text {
                text: title
                width: parent.width
                font.pixelSize: 28
                font.bold: true
                color: "#0F172A"
                wrapMode: Text.WordWrap
            }

            Text {
                text: subtitle
                width: parent.width
                font.pixelSize: 17
                color: "#475569"
                visible: subtitle !== ""
                wrapMode: Text.WordWrap
            }

            Text {
                text: root.text
                width: parent.width
                font.pixelSize: 15
                color: "#64748B"
                visible: root.text !== ""
                wrapMode: Text.WordWrap
            }

            Column {
                width: parent.width
                spacing: 6
                visible: listItems.length > 0

                Repeater {
                    model: listItems
                    Text {
                        text: "•  " + modelData
                        width: parent.width
                        font.pixelSize: 15
                        color: "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }
    }
}
