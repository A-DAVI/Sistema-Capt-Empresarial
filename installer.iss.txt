; ================================
; Instalador oficial do Captação Empresarial – Escritório 14D
; Desenvolvido por: Davi Cassoli Lira
; ================================

[Setup]
AppName=Captação Empresarial – Escritório 14D
AppVersion=1.0.0
AppPublisher=Grupo 14D
DefaultDirName={pf}\Grupo 14D\CaptacaoEmpresarial
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=installer
OutputBaseFilename=Instalador-CaptacaoEmpresarial
Compression=lzma
SolidCompression=yes
SetupIconFile=logo.ico
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "dist\CaptacaoEmpresarial14D.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Captação Empresarial – Escritório 14D"; Filename: "{app}\CaptacaoEmpresarial14D.exe"
Name: "{autodesktop}\Captação Empresarial – Escritório 14D"; Filename: "{app}\CaptacaoEmpresarial14D.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\CaptacaoEmpresarial14D.exe"; Description: "Executar o sistema após concluir"; Flags: nowait postinstall skipifsilent
