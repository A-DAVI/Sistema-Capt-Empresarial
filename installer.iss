; ================================
; Instalador oficial do Sistema-Capt-Empresarial
; Desenvolvedor: Davi Cassoli Lira
; Grupo 14D
; ================================

[Setup]
AppName=Sistema de Controle de Gastos Empresariais
AppVersion=1.0.0
AppPublisher=Grupo 14D
DefaultDirName={pf}\Grupo 14D\Sistema Capt Empresarial
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=installer
OutputBaseFilename=Instalador-Sistema-Capt-14D
Compression=lzma
SolidCompression=yes
SetupIconFile=Logo-Icon
WizardStyle=modern

[Files]
Source: "dist\SistemaCaptEmpresarial.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Sistema de Controle de Gastos Empresariais"; Filename: "{app}\SistemaCaptEmpresarial.exe"
Name: "{autodesktop}\Sistema de Controle de Gastos Empresariais"; Filename: "{app}\SistemaCaptEmpresarial.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\SistemaCaptEmpresarial.exe"; Description: "Executar o sistema após concluir"; Flags: nowait postinstall skipifsilent
