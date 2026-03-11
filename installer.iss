; ═══════════════════════════════════════════════════
; Script de Inno Setup para Mi Aplicación
; Genera: setup_miapp.exe
; ═══════════════════════════════════════════════════

[Setup]
AppName=Mi Aplicación
AppVersion=1.0.0
AppPublisher=Tu Nombre
DefaultDirName={autopf}\MiApp
DefaultGroupName=Mi Aplicación
OutputBaseFilename=setup_miapp
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\MiApp.exe

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
; El ejecutable principal (generado por PyInstaller)
Source: "dist\MiApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Mi Aplicación"; Filename: "{app}\MiApp.exe"
Name: "{group}\Desinstalar Mi Aplicación"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Mi Aplicación"; Filename: "{app}\MiApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MiApp.exe"; Description: "Iniciar Mi Aplicación"; Flags: nowait postinstall skipifsilent
