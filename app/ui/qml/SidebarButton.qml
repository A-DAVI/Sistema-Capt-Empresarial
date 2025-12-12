import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects 1.0

Item {
    id: root
    width: parent.width
    height: 48

    property string iconSource: ""
    property string title: ""
    property int pageIndex: 0
    property int currentPage: 0
    signal clicked()

    Rectangle {
        anchors.fill: parent
        radius: 8
        color: currentPage === pageIndex ? "#1E293B" : "transparent"

        MouseArea {
            anchors.fill: parent
            onClicked: root.clicked()
            cursorShape: Qt.PointingHandCursor
        }
    }

    // Ícone (preto original escondido)
    Image {
        id: iconImg
        source: iconSource
        width: 22
        height: 22
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.verticalCenter: parent.verticalCenter
        fillMode: Image.PreserveAspectFit
        visible: false
    }

    // Ícone pintado de branco
    ColorOverlay {
        anchors.fill: iconImg
        source: iconImg
        color: "white"
    }

    // Texto
    Text {
        text: title
        color: "white"
        anchors.left: iconImg.right
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        visible: title !== ""
        font.pixelSize: 14
    }
}
