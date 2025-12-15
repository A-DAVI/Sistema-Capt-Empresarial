import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Item {
    anchors.fill: parent

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: content.implicitHeight + 80
        clip: true

        Column {
            id: content
            width: parent.width
            spacing: 48
            padding: 32

            // ───────────────── HERO ─────────────────
            HeroSection { }

           // ───────────────── KPIs (ANIMADOS E VISÍVEIS) ─────────────────
            RowLayout {
                id: kpiRow
                spacing: 16
                Layout.fillWidth: true

                property bool startAnimation: false
                Component.onCompleted: startAnimation = true

                Repeater {
                    model: [
                        { title: "Total do mês", value: "R$ —" },
                        { title: "Mês anterior", value: "R$ —" },
                        { title: "Variação", value: "0.0%", valueColor: "#16A34A" },
                        { title: "Maior categoria", value: "—" }
                    ]

                    Item {
                        id: kpiItem

                        Layout.preferredWidth: 220
                        Layout.minimumWidth: 180
                        Layout.preferredHeight: 120
                        Layout.fillWidth: true

                        opacity: 0
                        y: 12

                        SummaryCard {
                            anchors.fill: parent
                            title: modelData.title
                            value: modelData.value
                            valueColor: modelData.valueColor ?? "#0F172A"
                        }

                        SequentialAnimation {
                            running: kpiRow.startAnimation

                            PauseAnimation {
                                duration: index * 90
                            }

                            ParallelAnimation {
                                OpacityAnimator {
                                    target: kpiItem
                                    from: 0
                                    to: 1
                                    duration: 260
                                    easing.type: Easing.OutCubic
                                }

                                YAnimator {
                                    target: kpiItem
                                    from: 12
                                    to: 0
                                    duration: 260
                                    easing.type: Easing.OutCubic
                                }
                            }
                        }
                    }
                }
                }



            // ───────────── AÇÕES RÁPIDAS ─────────────
            RowLayout {
                spacing: 16

                Repeater {
                    model: [
                        "Lançar despesa",
                        "Gestão de despesas",
                        "Exportar / Relatórios"
                    ]

                    Button {
                        text: modelData
                        height: 36
                        padding: 18

                        background: Rectangle {
                            radius: 10
                            color: hovered ? "#E0ECFF" : "#F1F5F9"
                            border.color: "#E2E8F0"
                        }

                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2563EB"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }

            // ───────────────── LANDING ─────────────────
            LandingSection { }
        }
    }
}
