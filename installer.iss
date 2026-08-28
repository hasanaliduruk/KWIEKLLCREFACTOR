; ============================================================================
; Operations Toolkit — Inno Setup installer script (Optimize Edilmiş)
; ============================================================================

#define MyAppName "KWIEK LLC WEBVIEW"
#define MyAppVersion "1.3.11"
#define MyAppPublisher "Kwiek LLC"
#define MyAppURL "https://github.com/hasanaliduruk/KWIEKLLCREFACTOR"
#define MyAppExeName "OperationsToolkit_Webview.exe"

[Setup]
AppId={{8F3C2A1B-6E4D-4C9A-9B21-7D5E8F0A1C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName=C:\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
SourceDir=.
OutputDir=Output
OutputBaseFilename=OperationsToolkit_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; 1. Programın temel dosyalarını kopyala (Settings klasörü HARİÇ veya mevcut dosyaları ezdirmeden)
Source: "dist\OperationsToolkit_Webview\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "Settings\*"

; 2. Settings klasöründeki dosyaları kopyala ANCAK kullanıcının halihazırda var olan ayarlarını ASLA EZME
Source: "dist\OperationsToolkit_Webview\Settings\*"; DestDir: "{app}\Settings"; Flags: ignoreversion confirmoverwrite recursesubdirs createallsubdirs onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{cmd}"; Parameters: "/c if not exist ""{app}\Settings"" mkdir ""{app}\Settings"""; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent