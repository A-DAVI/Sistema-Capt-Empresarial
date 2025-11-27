; Instalador oficial do Captacao Empresarial - Grupo 14D
; Desenvolvido por: Equipe 14D

[Setup]
AppName=CentralDeControle - GRUPO 14D
AppVersion=1.0.0
AppPublisher=Grupo 14D
DefaultDirName={pf}\Grupo 14D\CaptacaoEmpresarial
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=installer
OutputBaseFilename=CentralDeControle-GRUPO14D-Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=logo.ico
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "dist\INTERFACE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{autoprograms}\CentralDeControle - GRUPO 14D"; Filename: "{app}\CentralDeControle-GRUPO14D.exe"
Name: "{autodesktop}\CentralDeControle - GRUPO 14D"; Filename: "{app}\CentralDeControle-GRUPO14D.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\CentralDeControle-GRUPO14D.exe"; Description: "Executar o sistema apos concluir"; Flags: nowait postinstall skipifsilent
