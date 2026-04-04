; Setup.iss (FCP)
; Inno Setup Script for File Converter Pro
; Dual language support: French / English
; Complete uninstallation support

#define MyAppName "File Converter Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Prime Enterprises"
#define MyAppURL "https://github.com/Hyacinthe-primus/File-Converter-Pro"
#define MyAppExeName "File Converter Pro.exe"
#define MyAppId "{{C1E31023-8141-4243-96B2-D3AAC59CAC6F}}"
#define MyDistDir "dist\File Converter Pro"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoCopyright=© 2026 {#MyAppPublisher}. All rights reserved.
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=FileConverterPro_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
WizardStyle=modern
WizardSmallImageFile=installer_banner.bmp
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE\LICENSE.txt"
Name: "french";  MessagesFile: "compiler:Languages\French.isl"; LicenseFile: "LICENSE\LICENSE_FR.txt"

[CustomMessages]
french.AddAntivirusExclusion=Ajouter une exclusion Windows Defender (recommandé pour les performances)
english.AddAntivirusExclusion=Add Windows Defender exclusion (recommended for performance)
french.AppDescription=File Converter Pro - Le convertisseur de fichiers professionnel et rapide, entièrement gratuit
english.AppDescription=File Converter Pro - Fast professional file converter, made for free
french.AssocFileType=Associer les fichiers .fcproj avec File Converter Pro
english.AssocFileType=Associate .fcproj files with File Converter Pro

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "assocfileext"; Description: "{cm:AssocFileType}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Uninstallation icon
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; ONEDIR: exe + all DLLs and files from the dist folder
Source: "{#MyDistDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "{#MyAppExeName}"

; Quick Check utility
Source: "{#MyDistDir}\Quick Check.exe"; DestDir: "{app}"; Flags: ignoreversion

; Configuration and keys
Source: "file_converter_config.dat"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists('file_converter_config.dat')
Source: "file_converter_key.key"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists('file_converter_key.key')

; Databases (onlyifdoesntexist to avoid overwriting user data)
Source: "achievements.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist; Check: FileExists('achievements.db')
Source: "file_converter_stats.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist; Check: FileExists('file_converter_stats.db')
Source: "special_events.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist; Check: FileExists('special_events.db')

; License — only the selected language is installed
Source: "LICENSE\LICENSE.txt";    DestDir: "{app}"; Flags: ignoreversion; Check: IsEnglish()
Source: "LICENSE\LICENSE_FR.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: IsFrench()

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Comment: "{cm:AppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Comment: "{cm:AppDescription}"; Tasks: desktopicon

[Registry]
; Association extension .fcproj
Root: HKCU; Subkey: "Software\Classes\.fcproj"; ValueType: string; ValueName: ""; ValueData: "FileConverterPro.Project"; Flags: uninsdeletevalue; Tasks: assocfileext
Root: HKCU; Subkey: "Software\Classes\FileConverterPro.Project"; ValueType: string; ValueName: ""; ValueData: "File Converter Pro Project"; Flags: uninsdeletekey; Tasks: assocfileext
Root: HKCU; Subkey: "Software\Classes\FileConverterPro.Project\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico,0"; Tasks: assocfileext
Root: HKCU; Subkey: "Software\Classes\FileConverterPro.Project\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: assocfileext
Root: HKCU; Subkey: "Software\Classes\FileConverterPro.Project\shell\open"; ValueType: string; ValueName: "WorkingDirectory"; ValueData: "{app}"; Tasks: assocfileext

[Run]
; Pass the installer language code to the exe on first launch.
; This ensures the app starts in the language the user chose during installation,
; even if the config file does not exist yet (WriteLanguageConfig handles the
; case where the user unchecks "Launch app" and opens the app later).
Filename: "{app}\{#MyAppExeName}"; Parameters: "--lang {code:GetLangCode}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{localappdata}\{#MyAppName}"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
; Delete folder in LocalAppData
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}"

[Code]
var
  AntivirusExclusionCheckbox: TNewCheckBox;

function IsEnglish(): Boolean;
begin
  Result := ActiveLanguage() = 'english';
end;

function IsFrench(): Boolean;
begin
  Result := ActiveLanguage() = 'french';
end;

{ Maps the Inno Setup language name (e.g. "french") to the short code
  expected by the app's --lang flag (e.g. "fr").
  Add more languages here as needed. }
function GetLangCode(Param: String): String;
begin
  if ActiveLanguage() = 'french' then
    Result := 'fr'
  else
    Result := 'en';
end;

{ Writes a minimal plain-text JSON config containing only the selected
  language code. This guarantees the app starts in the correct language
  even when the user never launches it right after installation.

  The file is written only when no config exists yet (fresh install).
  On the first real launch, AppBootstrap reads the language from this
  file, then re-saves the full config in encrypted form — so the
  plain-text file is automatically replaced. }
procedure WriteLanguageConfig();
var
  ConfigPath: String;
  JsonContent: String;
begin
  // Config lives next to the exe — same folder the app uses at runtime
  // (PrivilegesRequired=lowest means {app} is in %LocalAppData%\Programs,
  // not Program Files, so there are no permission issues here).
  ConfigPath := ExpandConstant('{app}\file_converter_config.dat');

  if not FileExists(ConfigPath) then
  begin
    JsonContent := '{"language": "' + GetLangCode('') + '"}';
    SaveStringToFile(ConfigPath, JsonContent, False);
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsWin64 then begin
    MsgBox('This application requires Windows 64-bit.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure InitializeWizard;
begin
  AntivirusExclusionCheckbox := TNewCheckBox.Create(WizardForm);
  AntivirusExclusionCheckbox.Parent := WizardForm.ReadyMemo.Parent;
  AntivirusExclusionCheckbox.Top := WizardForm.ReadyMemo.Top + WizardForm.ReadyMemo.Height + ScaleY(8);
  AntivirusExclusionCheckbox.Left := WizardForm.ReadyMemo.Left;
  AntivirusExclusionCheckbox.Width := WizardForm.ReadyMemo.Width;
  AntivirusExclusionCheckbox.Height := ScaleY(17);
  AntivirusExclusionCheckbox.Caption := CustomMessage('AddAntivirusExclusion');
  AntivirusExclusionCheckbox.Checked := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  AppPath: String;
begin
  if CurStep = ssPostInstall then begin
    ForceDirectories(ExpandConstant('{localappdata}\{#MyAppName}'));

    // Write the chosen language to the config file before the exe is ever
    // launched. Covers the case where the user unchecks "Launch app" at the
    // end of the installer — the --lang flag in [Run] would never fire then.
    WriteLanguageConfig();

    if AntivirusExclusionCheckbox.Checked then begin
      AppPath := ExpandConstant('{app}');
      Exec('powershell.exe',
            '-NoProfile -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath ''' + AppPath + ''' -ErrorAction Stop } catch { }"',
            '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
