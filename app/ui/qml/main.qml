import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Basic 2.15
import QtQuick.Layouts 1.15
import "."

Window {
    id: window
    width: 1200
    height: 720
    visible: true
    title: "Central de Controle - Grupo 14D"

    Rectangle {
        anchors.fill: parent
        color: "#F5F7FA"

        Row {
            anchors.fill: parent

            Sidebar {
                id: sidebar
                anchors.top: parent.top
                anchors.bottom: parent.bottom
            }

            Rectangle {
                id: contentArea
                color: "#F5F7FA"
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                width: parent.width - sidebar.width

                HomePage {
                    id: homePage
                }
            }
        }
    }
}
