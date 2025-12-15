import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

ApplicationWindow {
    id: app
    visible: true
    width: 1280
    height: 800
    title: "Central de Controle - Grupo 14D"

    StackView {
        id: stack
        anchors.fill: parent

        initialItem: LoginPage {
            onLoginSuccess: stack.push("HomePage.qml")
        }
    }
}
