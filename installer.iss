; ================================
; Instalador oficial do Sistema-Capt-Empresarial
; Desenvolvedor: Davi Cassoli Lira
; Grupo 14D
; ================================

[Setup]
AppName=Captação Empresarial - Escritório 14D
AppVersion=1.0.0
AppPublisher=Grupo 14D
DefaultDirName={pf}\Grupo14D\CaptacaoEmpresarial14D
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=installer
OutputBaseFilename=Instalador-CaptacaoEmpresarial14D
Compression=lzma
SolidCompression=yes
SetupIconFile=logo.ico
WizardStyle=modern

[Files]
Source: "dist\CaptacaoEmpresarial14D.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Captação Empresarial 14D"; Filename: "{app}\CaptacaoEmpresarial14D.exe"
Name: "{autodesktop}\Captação Empresarial 14D"; Filename: "{app}\CaptacaoEmpresarial14D.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\CaptacaoEmpresarial14D.exe"; Description: "Executar o sistema após concluir"; Flags: nowait postinstall skipifsilent
