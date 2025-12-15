import QtQuick 2.15
import QtQuick.Layouts 1.15
import "."

Item {
    id: root
    width: parent.width
    implicitHeight: column.implicitHeight + 120

    Column {
        id: column
        width: Math.min(parent.width, 1100)
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 120

        // ───────────────── BLOCO 1 ─────────────────
        LandingBlock {
            title: "Bem-vindo à Central de Controle — Grupo 14D"
            subtitle: "Inteligência contábil e financeira aplicada ao dia a dia."
            text: "A Central de Controle foi desenvolvida para simplificar o acompanhamento financeiro das empresas atendidas pelo Grupo 14D. Aqui, informações antes dispersas passam a ser organizadas em um único ambiente, permitindo mais clareza, controle e segurança na gestão das despesas e indicadores."
            illustrationSource: "../assets/illustrations/teamcollaboration.png"
            imageScale: 1.2
        }

        // ───────────────── BLOCO 2 ─────────────────
        LandingBlock {
            title: "Quem somos"
            subtitle: "Experiência contábil aliada à tecnologia."
            text: "O Grupo 14D atua com foco em contabilidade, gestão e consultoria, apoiando empresas que buscam organização financeira e tomada de decisão baseada em dados. Nosso trabalho une conhecimento técnico, proximidade com o cliente e soluções tecnológicas que facilitam a rotina operacional."
            alignRight: true
            illustrationSource: "../assets/illustrations/dashboard_stats.png"
            imageScale: 1.2
        }

        // ───────────────── BLOCO 3 ─────────────────
        LandingBlock {
            title: "Por que usar este sistema?"
            subtitle: "Um ponto único de controle financeiro."
            text: "Este sistema foi criado para centralizar informações financeiras de forma padronizada e confiável. Ele reduz erros manuais, melhora a organização dos dados e oferece uma visão clara do comportamento das despesas ao longo do tempo."
            listItems: [
                "Centralização de lançamentos e categorias com validação contábil.",
                "Dashboards claros para análise rápida dos números.",
                "Relatórios executivos prontos para auditoria e diretoria.",
                "Histórico completo de empresas, períodos e fornecedores."
            ]
            illustrationSource: "../assets/illustrations/desktop.png"
            imageScale: 1.2
        }

        // ───────────────── BLOCO 4 ─────────────────
        LandingBlock {
            title: "Benefícios imediatos"
            subtitle: "Mais controle desde o primeiro uso."
            text: "Desde os primeiros lançamentos, o sistema já entrega ganhos práticos. As informações ficam mais acessíveis, os comparativos se tornam claros e o acompanhamento financeiro passa a ser feito de forma contínua, não apenas no fechamento do mês."
            listItems: [
                "Visão consolidada de despesas por período e categoria.",
                "Indicadores de variação mensal e impacto de custos.",
                "Exportações rápidas e padronizadas.",
                "Menos retrabalho e mais consistência nos dados."
            ]
            illustrationSource: "../assets/illustrations/win.png"
            imageScale: 1.3
            alignRight: true
        }

        // ───────────────── BLOCO 5 ─────────────────
        LandingBlock {
            title: "Como ajuda seu time"
            subtitle: "Informação certa para cada área."
            text: "A Central de Controle atende diferentes áreas da empresa, oferecendo informações específicas para cada necessidade. Isso facilita o alinhamento entre financeiro, contabilidade e gestão, reduzindo ruídos e aumentando a eficiência."
            listItems: [
                "Financeiro: controle de custos, comparativos e histórico.",
                "Contabilidade: lançamentos padronizados e organizados.",
                "Gestão: indicadores claros para decisões mais rápidas."
            ]
            illustrationSource: "../assets/illustrations/help.png"
            imageScale: 1.0
        }

        // ───────────────── BLOCO 6 ─────────────────
        LandingBlock {
            title: "Suporte e acompanhamento"
            subtitle: "Você não utiliza o sistema sozinho."
            text: "Além da ferramenta, o Grupo 14D oferece acompanhamento próximo para garantir que o sistema esteja alinhado às rotinas da sua empresa. Nossa equipe está disponível para orientar ajustes, esclarecer dúvidas e apoiar a evolução do uso da plataforma."
            illustrationSource: "../assets/illustrations/suporte.png"
            imageScale: 1.1
            alignRight: true
        }

        // ───────────── LOGOS ─────────────
        Column {
            width: parent.width
            spacing: 16
            anchors.horizontalCenter: parent.horizontalCenter

            Rectangle {
                width: 120
                height: 2
                radius: 1
                color: "#E5E7EB"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Empresas que utilizam a Central de Controle 14D"
                font.pixelSize: 16
                font.weight: Font.Medium
                color: "#475569"
                horizontalAlignment: Text.AlignHCenter
                width: parent.width
            }

            CompanyLogoCarousel {
                width: parent.width
                height: 64
                logos: [
                    "../assets/logos/logo1.png",
                    "../assets/logos/logo2.png",
                    "../assets/logos/logo3.png",
                    "../assets/logos/logo4.png",
                    "../assets/logos/logo5.png",
                    "../assets/logos/logo6.png"
                ]
            }
        }

        // ───────────────── CTA FINAL ─────────────────
        Column {
            width: parent.width
            spacing: 16
            anchors.horizontalCenter: parent.horizontalCenter

            Rectangle {
                width: 140
                height: 4
                radius: 2
                color: "#E0ECFF"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Pronto para registrar uma nova despesa ou acompanhar seus resultados?"
                font.pixelSize: 22
                font.bold: true
                color: "#0F172A"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width * 0.7
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Utilize o menu lateral para acessar as funcionalidades e iniciar o controle financeiro."
                font.pixelSize: 15
                color: "#475569"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width * 0.7
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
