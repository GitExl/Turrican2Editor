[Tasks]
Name: desktopicon; Description: Create a desktop icon; Flags: unchecked

[Files]
Source: .\build\exe.win32-2.7\*.*; DestDir: {app}; Flags: recursesubdirs createallsubdirs

[Icons]
Name: {group}\Turrican II Editor; Filename: {app}\turrican2editor.exe; WorkingDir: {app}; IconFilename: {app}\res\icon-diamond.ico; IconIndex: 0
Name: {userdesktop}\Turrican II Editor; Filename: {app}\turrican2editor.exe; WorkingDir: {app}; IconFilename: {app}\res\icon-diamond.ico; IconIndex: 0; Tasks: " desktopicon"
Name: {group}\{cm:UninstallProgram, Turrican II Editor}; Filename: {uninstallexe}

[Setup]
InternalCompressLevel=ultra64
SolidCompression=true
AppName=Turrican II Editor
AppVerName=Turrican II Editor 1.0.1
DefaultDirName={pf}\Turrican II Editor
AlwaysUsePersonalGroup=false
ShowLanguageDialog=no
AppVersion=1.0.1
UninstallDisplayIcon={app}\turrican2editor.exe
UninstallDisplayName=Turrican II Editor
AppendDefaultGroupName=true
DefaultGroupName=Turrican II Editor
Compression=lzma/ultra64
OutputDir=.
SourceDir=.
OutputBaseFilename=turrican2editor-setup-1.0.1
AllowNoIcons=true
PrivilegesRequired=admin
ChangesAssociations=true
InfoBeforeFile=
LicenseFile=LICENSE
FlatComponentsList=true
UninstallLogMode=overwrite
LanguageDetectionMethod=none
WizardImageStretch=false
RestartIfNeededByRun=false
AppID={{A8A56AC6-E82B-49AD-9093-5AC204830F89}

[Run]
Filename: {app}\turrican2editor.exe; WorkingDir: {app}; Description: Run Turrican II Editor; Flags: nowait postinstall hidewizard skipifsilent

[UninstallDelete]
Name: {app}\res; Type: filesandordirs
Name: {app}\entities; Type: filesandordirs
Name: {app}\fonts; Type: filesandordirs
Name: {app}\*.*; Type: files
Name: {app}; Type: dirifempty
