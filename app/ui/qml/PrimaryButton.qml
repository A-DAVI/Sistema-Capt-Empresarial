import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: root
    height: 44

    background: Rectangle {
        radius: 10
        color: root.hovered ? "#1D4ED8" : "#2563EB"
    }

    contentItem: Text {
        text: root.text
        color: "white"
        font.pixelSize: 14
        font.weight: Font.Bold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
