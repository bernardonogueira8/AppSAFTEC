[Setup]
AppName=SAFTEC
AppVersion=1.0.0
AppId={{4fd8628c-3d33-49ee-8505-a0889bbe77a4}}
PrivilegesRequired=lowest
DefaultDirName={localappdata}\SAFTEC
UsedUserAreasWarning=no
OutputDir=Output
OutputBaseFilename=SAFTEC_Setup_1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Essencial para detectar versão anterior
UninstallDisplayName=SAFTEC
CreateUninstallRegKey=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\build\windows\SAFTEC-app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\ms-playwright\*"; DestDir: "{app}\ms-playwright"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Limpa arquivos antigos do app antes de instalar novo
Type: filesandordirs; Name: "{app}\lib"
Type: filesandordirs; Name: "{app}\data"

[Icons]
Name: "{userprograms}\SAFTEC"; Filename: "{app}\SAFTEC-app.exe"
Name: "{userdesktop}\SAFTEC"; Filename: "{app}\SAFTEC-app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SAFTEC-app.exe"; Description: "{cm:LaunchProgram,SAFTEC}"; Flags: nowait postinstall skipifsilent

[Code]
// Desinstala versão anterior automaticamente antes de instalar
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  UninstPath: String;
begin
  if CurStep = ssInstall then begin
    UninstPath := ExpandConstant('{localappdata}\SAFTEC\unins000.exe');
    if FileExists(UninstPath) then begin
      Exec(UninstPath, '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;