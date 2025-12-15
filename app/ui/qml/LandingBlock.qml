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

    // ─── PROPRIEDADES ───
    property string title: ""
    property string subtitle: ""
    property string text: ""
    property var listItems: []
    property bool alignRight: false

    property url illustrationSource: ""
    property real imageScale: 1.0

    Row {
        width: parent.width
        spacing: 80
        anchors.top: parent.top
        anchors.topMargin: 40

        // ───────── TEXTO ESQUERDA ─────────
        Column {
            id: textLeft
            width: parent.width * 0.45
            spacing: 14
            visible: !alignRight

            // TÍTULO
            Text {
                text: title
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 34
                font.weight: Font.SemiBold
                color: "#0F172A"
                wrapMode: Text.WordWrap
            }

            // SUBTÍTULO
            Text {
                text: subtitle
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#334155"
                visible: subtitle !== ""
                wrapMode: Text.WordWrap
            }

            // TEXTO DESCRITIVO
            Text {
                text: root.text
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 15
                font.weight: Font.Normal
                lineHeight: 1.4
                color: "#64748B"
                visible: root.text !== ""
                wrapMode: Text.WordWrap
            }

            // LISTA
            Column {
                width: parent.width
                spacing: 8
                visible: listItems.length > 0

                Repeater {
                    model: listItems
                    Text {
                        text: "•  " + modelData
                        width: parent.width
                        font.family: "Inter"
                        font.pixelSize: 15
                        font.weight: Font.Normal
                        color: "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // ───────── ILUSTRAÇÃO ─────────
        Item {
            id: visualBox
            width: 420
            height: 320

            Image {
                anchors.centerIn: parent
                source: illustrationSource
                fillMode: Image.PreserveAspectFit
                smooth: true
                visible: illustrationSource !== ""
                width: parent.width * imageScale
                height: parent.height * imageScale
            }

            Text {
                anchors.centerIn: parent
                text: "14D"
                font.pixelSize: 88
                font.bold: true
                color: "#0D6EFD"
                opacity: illustrationSource === "" ? 0.06 : 0
            }
        }

        // ───────── TEXTO DIREITA ─────────
        Column {
            id: textRight
            width: parent.width * 0.45
            spacing: 14
            visible: alignRight

            Text {
                text: title
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 34
                font.weight: Font.SemiBold
                color: "#0F172A"
                wrapMode: Text.WordWrap
            }

            Text {
                text: subtitle
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#334155"
                visible: subtitle !== ""
                wrapMode: Text.WordWrap
            }

            Text {
                text: root.text
                width: parent.width
                font.family: "Inter"
                font.pixelSize: 15
                font.weight: Font.Normal
                lineHeight: 1.4
                color: "#64748B"
                visible: root.text !== ""
                wrapMode: Text.WordWrap
            }

            Column {
                width: parent.width
                spacing: 8
                visible: listItems.length > 0

                Repeater {
                    model: listItems
                    Text {
                        text: "•  " + modelData
                        width: parent.width
                        font.family: "Inter"
                        font.pixelSize: 15
                        font.weight: Font.Normal
                        color: "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }
    }
}
