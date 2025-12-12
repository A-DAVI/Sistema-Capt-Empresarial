import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: parent ? parent.width : 800
    height: 72

    // lista de caminhos das logos
    property var logos: []

    // quanto maior, mais lento
    property int scrollDuration: 18000

    // estilo
    property int logoHeight: 44
    property int spacing: 48
    property real baseOpacity: 0.75
    property real hoverOpacity: 1.0

    // container com recorte
    Item {
        id: clipper
        anchors.fill: parent
        clip: true

        Row {
            id: logoRow
            spacing: root.spacing
            height: parent.height
            y: Math.round((parent.height - root.logoHeight) / 2)

            Repeater {
                model: root.logos.length > 0 ? root.logos.concat(root.logos) : []
                delegate: Image {
                    source: modelData
                    height: root.logoHeight
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    opacity: root.baseOpacity

                    Behavior on opacity {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.ArrowCursor
                        onEntered: parent.opacity = root.hoverOpacity
                        onExited: parent.opacity = root.baseOpacity
                    }
                }
            }
        }

        // animação contínua
        NumberAnimation {
            id: marquee
            target: logoRow
            property: "x"
            from: 0
            to: -(logoRow.width / 2)
            duration: root.scrollDuration
            loops: Animation.Infinite
            running: root.logos.length > 0
        }

        // garante reset suave quando mudar lista/tamanho
        onWidthChanged: logoRow.x = 0
    }
}
