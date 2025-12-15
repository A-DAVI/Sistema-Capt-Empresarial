import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    width: 360
    spacing: 16

    signal loginSuccess()

    Text {
        text: "Acesso ao sistema"
        font.pixelSize: 22
        font.weight: Font.Bold
        color: "#0F172A"
    }

    ComboBox {
        width: parent.width
        model: ["Empresa A", "Empresa B"]
        currentIndex: -1
    }

    TextField {
        id: userField
        width: parent.width
        placeholderText: "Usuário"
    }

    TextField {
        id: passField
        width: parent.width
        placeholderText: "Senha"
        echoMode: TextInput.Password
        passwordMaskDelay: 300
    }

    Button {
        text: "Entrar"
        height: 44
        width: parent.width
        enabled: userField.text.length > 0 && passField.text.length > 0
        opacity: enabled ? 1 : 0.6

        background: Rectangle {
            radius: 10
            color: "#2563EB"
        }

        contentItem: Text {
            text: parent.text
            color: "white"
            font.pixelSize: 14
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            if (userField.text === "admin" && passField.text === "123") {
                loginSuccess()
            }
        }
    }

    Text {
        text: "Esqueci minha senha"
        font.pixelSize: 12
        color: "#2563EB"
        horizontalAlignment: Text.AlignHCenter
        width: parent.width
    }
}
