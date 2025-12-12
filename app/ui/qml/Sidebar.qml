import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects 1.0
import "."

Rectangle {
    id: sidebar
    width: expanded ? 220 : 80
    color: "#0F172A"
    anchors.top: parent.top
    anchors.bottom: parent.bottom

    property bool expanded: false
    property int currentPage: 0
    signal pageSelected(int index)

    Behavior on width {
        NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
    }

    // BOTÃO HAMBÚRGUER
    MouseArea {
        id: toggleArea
        width: sidebar.width
        height: 56
        anchors.top: parent.top
        onClicked: sidebar.expanded = !sidebar.expanded
        cursorShape: Qt.PointingHandCursor
    }

    // Ícone bruto
    Image {
        id: iconRaw
        source: sidebar.expanded ? "icons/close.svg" : "icons/menu.svg"
        width: 24
        height: 24
        anchors.left: parent.left
        anchors.leftMargin: 28
        anchors.verticalCenter: toggleArea.verticalCenter
        fillMode: Image.PreserveAspectFit
        visible: false
    }

    // Ícone com overlay branco
    ColorOverlay {
        anchors.fill: iconRaw
        source: iconRaw
        color: "white"
    }

    // MENU
    Column {
        anchors.top: toggleArea.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 6
        padding: 14

        SidebarButton {
            iconSource: "icons/house.svg"
            title: sidebar.expanded ? "Início" : ""
            pageIndex: 0
            currentPage: sidebar.currentPage
            onClicked: sidebar.pageSelected(pageIndex)
        }

        SidebarButton {
            iconSource: "icons/wallet.svg"
            title: sidebar.expanded ? "Despesas" : ""
            pageIndex: 1
            currentPage: sidebar.currentPage
            onClicked: sidebar.pageSelected(pageIndex)
        }

        SidebarButton {
            iconSource: "icons/reports.svg"
            title: sidebar.expanded ? "Relatórios" : ""
            pageIndex: 2
            currentPage: sidebar.currentPage
            onClicked: sidebar.pageSelected(pageIndex)
        }

        SidebarButton {
            iconSource: "icons/settings.svg"
            title: sidebar.expanded ? "Configurações" : ""
            pageIndex: 3
            currentPage: sidebar.currentPage
            onClicked: sidebar.pageSelected(pageIndex)
        }
    }
}
