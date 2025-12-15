import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    anchors.fill: parent

    signal loginSuccess()

    Row {
        anchors.fill: parent

        Rectangle {
            width: parent.width * 0.45
            color: "#0B1220"

            Column {
                anchors.centerIn: parent
                spacing: 20
                width: parent.width * 0.75

                Image {
                    source: "../assets/logo_empresa.png"
                    width: 160
                    fillMode: Image.PreserveAspectFit
                }

                Text {
                    text: "Grupo 14D"
                    font.pixelSize: 26
                    font.weight: Font.Bold
                    color: "white"
                }

                Text {
                    text: "Central de Controle Financeiro"
                    font.pixelSize: 15
                    color: "#CBD5E1"
                }

                Image {
                    source: "../assets/illustrations/login.png"
                    width: parent.width
                    fillMode: Image.PreserveAspectFit
                }
            }
        }

        Rectangle {
            width: parent.width * 0.55
            color: "white"

            LoginForm {
                anchors.centerIn: parent

                onLoginSuccess: {
                    loginSuccess()
                }
            }
        }
    }
}
