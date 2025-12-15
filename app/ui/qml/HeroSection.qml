import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: parent.width
    height: 280

    property bool startAnimation: false
    Component.onCompleted: startAnimation = true

    Row {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 48

        // ───────── TEXTO ─────────
        Column {
            id: textBlock
            width: parent.width * 0.55
            spacing: 12

            opacity: 0
            y: 20

            Text {
                text: "Bem-vindo de volta, Davi"
                font.pixelSize: 16
                font.weight: Font.Medium
                color: "#64748B"
            }

            Text {
                text: "Central de Controle Financeiro"
                font.pixelSize: 36
                font.weight: Font.Bold
                color: "#0F172A"
                wrapMode: Text.WordWrap
            }

            Text {
                text: "Gerencie despesas, acompanhe indicadores e tenha total clareza para decisões financeiras no dia a dia."
                font.pixelSize: 16
                color: "#64748B"
                wrapMode: Text.WordWrap
                width: parent.width * 0.95
            }

            RowLayout {
                spacing: 12
                Layout.topMargin: 8

                // CTA PRINCIPAL
                Button {
                    text: "Lançar despesa"
                    hoverEnabled: true
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 150

                    background: Rectangle {
                        radius: 10
                        color: hovered ? "#1D4ED8" : "#2563EB"
                    }

                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                // CTA SECUNDÁRIO
                Button {
                    text: "Ver relatórios"
                    hoverEnabled: true
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 140

                    background: Rectangle {
                        radius: 10
                        color: hovered ? "#EFF6FF" : "transparent"
                        border.color: "#2563EB"
                        border.width: 1
                    }

                    contentItem: Text {
                        text: parent.text
                        color: "#2563EB"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }

            }

            // animação do texto
            ParallelAnimation {
                running: startAnimation

                OpacityAnimator {
                    target: textBlock
                    from: 0
                    to: 1
                    duration: 400
                    easing.type: Easing.OutCubic
                }

                YAnimator {
                    target: textBlock
                    from: 20
                    to: 0
                    duration: 400
                    easing.type: Easing.OutCubic
                }
            }
        }

        // ───────── ILUSTRAÇÃO ─────────
        Item {
            id: imageBlock
            width: parent.width * 0.45
            height: parent.height

            opacity: 0
            x: 40

            Image {
                anchors.centerIn: parent
                source: "../assets/illustrations/hero.png"
                fillMode: Image.PreserveAspectFit
                width: parent.width
            }

            // animação da imagem
            ParallelAnimation {
                running: startAnimation

                OpacityAnimator {
                    target: imageBlock
                    from: 0
                    to: 1
                    duration: 450
                    easing.type: Easing.OutCubic
                }

                XAnimator {
                    target: imageBlock
                    from: 40
                    to: 0
                    duration: 450
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
}
