; Instalador oficial do Captacao Empresarial - Grupo 14D
; Desenvolvido por: Equipe 14D

[Setup]
AppName=Controle - GRUPO 14D
AppVersion=1.0.0
AppPublisher=Grupo 14D
DefaultDirName={pf}\Grupo 14D\CaptacaoEmpresarial
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=installer
OutputBaseFilename=Controle - GRUPO 14D
Compression=lzma
SolidCompression=yes
SetupIconFile=logo.ico
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "dist\INTERFACE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{autoprograms}\Controle - GRUPO 14D"; Filename: "{app}\CaptacaoEmpresarial.exe"
Name: "{autodesktop}\Controle - GRUPO 14D"; Filename: "{app}\CaptacaoEmpresarial.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\CaptacaoEmpresarial.exe"; Description: "Executar o sistema apos concluir"; Flags: nowait postinstall skipifsilent
