; ============================================================================
; Operations Toolkit — Inno Setup installer script
;
; Build the app first:  build_shared.bat   (outputs dist\OperationsToolkit_Webview)
; Then compile this script with Inno Setup (ISCC.exe) to produce
;   Output\OperationsToolkit_Setup.exe
;
; The installer places the onedir bundle under Program Files, writes a
; Start Menu + Desktop shortcut, and registers an uninstaller. The app's
; built-in updater downloads a newer copy of THIS setup .exe from GitHub
; Releases and runs it silently (/SILENT), which overwrites the install.
; ============================================================================

#define MyAppName "Operations Toolkit"
#define MyAppVersion "1.2.4"
#define MyAppPublisher "Kwiek LLC"
#define MyAppURL "https://github.com/hasali2603/KWIEKLLC"
#define MyAppExeName "OperationsToolkit_Webview.exe"

[Setup]
; NOTE: The AppId value identifies the application uniquely. Do not change
; it after shipping the first release — changing it breaks silent upgrades.
AppId={{8F3C2A1B-6E4D-4C9A-9B21-7D5E8F0A1C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; The onedir build lives in dist\OperationsToolkit_Webview
SourceDir=.
OutputDir=Output
OutputBaseFilename=OperationsToolkit_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Let a running instance be replaced during a silent update
CloseApplications=yes
RestartApplications=no
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
; SignTool is invoked by build_shared.bat via /Sinnosetup_sign=... when a
; cert is configured. The placeholder below is overridden at build time.
SignTool=innosetup_sign "signtool.exe" sign /fd sha256 /tr http://timestamp.digicert.com /td sha256 $f

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Recursively pull in the whole onedir bundle (exe + _internal + assets + Settings)
Source: "dist\OperationsToolkit_Webview\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
; The app stores its Settings next to the exe; make sure the folder exists.
Filename: "{cmd}"; Parameters: "/c if not exist ""{app}\Settings"" mkdir ""{app}\Settings"""; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
