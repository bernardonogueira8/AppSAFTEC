; Script do Inno Setup para o projeto SAFTEC
; Desenvolvido para: Bernardo Silva (Data Science / ADS)

[Setup]
AppName=SAFTEC
AppVersion=1.0.0
; Define que a instalação é para o usuário logado (não pede senha de admin)
PrivilegesRequired=lowest
; Instala na pasta local do usuário (C:\Users\Nome\AppData\Local\SAFTEC)
DefaultDirName={localappdata}\SAFTEC
; Remove o aviso de que não está instalando em 'Arquivos de Programas'
UsedUserAreasWarning=no

; Pasta onde o .exe do instalador será gerado
OutputDir=Output
OutputBaseFilename=SAFTEC_Setup_
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
; Opção para o usuário criar ou não o atalho
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ajustado para sua estrutura da imagem (build\windows)
Source: "..\build\windows\SAFTEC-app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
; O {userprograms} e {userdesktop} garantem que os atalhos fiquem apenas no perfil do usuário
Name: "{userprograms}\SAFTEC"; Filename: "{app}\SAFTEC-app.exe"
Name: "{userdesktop}\SAFTEC"; Filename: "{app}\SAFTEC-app.exe"; Tasks: desktopicon

[Run]
; Abre o SAFTEC automaticamente após a instalação
Filename: "{app}\SAFTEC-app.exe"; Description: "{cm:LaunchProgram,SAFTEC}"; Flags: nowait postinstall skipifsilent