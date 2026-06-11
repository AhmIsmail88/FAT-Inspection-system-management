; ─────────────────────────────────────────────────────────────────────────────
; HAC FAT & Inspection System — Inno Setup Script
; Produces: HAC_FAT_System_Setup.exe
;
; Requirements:
;   - Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)  — free
;   - PyInstaller build output in: dist\HAC_FAT_System\
;
; How to build:
;   1. Run PyInstaller first:   pyinstaller fat_system.spec
;   2. Open this file in Inno Setup Compiler
;   3. Click Build → Compile
;   4. Output: installer\HAC_FAT_System_Setup.exe
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "HAC FAT & Inspection System"
#define AppVersion   "1.0.0"
#define AppPublisher "HAC — Ahmed Hassanin"
#define AppExeName   "HAC_FAT_System.exe"
#define AppFolder    "HAC_FAT_System"

[Setup]
; Basic info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=

; Install location
DefaultDirName={autopf}\{#AppFolder}
DefaultGroupName={#AppName}
AllowNoIcons=yes

; Output
OutputDir=installer
OutputBaseFilename=HAC_FAT_System_Setup_v{#AppVersion}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
WizardStyle=modern
WizardSmallImageFile=assets\logo.bmp
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Min Windows version: Windows 10
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Create a Desktop shortcut";     GroupDescription: "Additional icons:"; Flags: checked
Name: "startmenuicon";  Description: "Create a Start Menu shortcut";  GroupDescription: "Additional icons:"; Flags: checked

[Files]
; Main application files from PyInstaller output
Source: "dist\{#AppFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Desktop shortcut
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}";  Tasks: desktopicon;   IconFilename: "{app}\{#AppExeName}"
; Start Menu
Name: "{group}\{#AppName}";        Filename: "{app}\{#AppExeName}";  Tasks: startmenuicon
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; \
  Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any .pyc files left behind
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThe database is stored on the company server:%n%nV:\Fat Test (Infra - HUB)\DB%n%nPlease make sure you have access to this path before continuing.%n%nClick Next to continue, or Cancel to exit.

[Code]
// ─── Check server path is accessible before installing ─────────────────────
function ServerPathAccessible(): Boolean;
var
  ServerPath: String;
begin
  ServerPath := 'V:\Fat Test (Infra - HUB)\DB';
  Result := DirExists(ServerPath) or FileExists(ServerPath + '\fat_system.db');
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not ServerPathAccessible() then
  begin
    if MsgBox(
      'Warning: The server path could not be reached:' + #13#10 +
      'V:\Fat Test (Infra - HUB)\DB' + #13#10#13#10 +
      'The application will use a local folder instead.' + #13#10#13#10 +
      'Continue with installation?',
      mbConfirmation, MB_YESNO
    ) = IDNO then
      Result := False;
  end;
end;
