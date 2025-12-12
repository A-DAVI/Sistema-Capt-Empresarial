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
            Column {
                spacing: 6

                Text {
                    text: "Bem-vindo de volta, Davi!"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#0F172A"
                }

                Text {
                    text: "Gerencie suas despesas e acompanhe seus resultados de forma intuitiva e inteligente."
                    font.pixelSize: 16
                    color: "#4B5563"
                    width: parent.width * 0.7
                    wrapMode: Text.WordWrap
                }
            }

            // ───────────────── KPIs ─────────────────
            Row {
                spacing: 16

                SummaryCard { title: "Total do mês"; value: "R$ —" }
                SummaryCard { title: "Mês anterior"; value: "R$ —" }
                SummaryCard { title: "Variação"; value: "0.0%"; valueColor: "#16A34A" }
                SummaryCard { title: "Maior categoria"; value: "—" }
            }

            // ───────────── AÇÕES RÁPIDAS (REFINADO) ─────────────
            Row {
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
                            color: "#0D6EFD"
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
