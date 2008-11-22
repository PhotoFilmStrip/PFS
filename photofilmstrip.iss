
[Setup]
AppName           = PhotoFilmStrip
AppPublisher      = Jens G�pfert
AppPublisherURL   = http://photostoryx.sourceforge.net
AppCopyright      = Copyright (C) 2008 Jens G�pfert
AppVerName        = PhotoFilmStrip 0.95
AppVersion        = 0.95
VersionInfoVersion= 0.9.5.0
DefaultDirName    = {pf}\PhotoFilmStrip
DefaultGroupName  = PhotoFilmStrip
UninstallDisplayIcon={app}\bin\PhotoFilmStrip.exe
OutputDir=release
OutputBaseFilename = setup_photofilmstrip
LicenseFile       = copying
WizardSmallImageFile=res\icon\photofilmstrip.bmp
WizardImageFile=compiler:WizModernImage-IS.bmp
;compression=none

[Files]
Source: "dist\*";                   DestDir: "{app}";                     Flags: recursesubdirs;  
Source: "win32ExtBin\mjpegtools\*"; DestDir: "{app}\extBin\mjpegtools";   Flags: recursesubdirs;  
Source: "win32ExtBin\mplayer\*";    DestDir: "{app}\extBin\mplayer";      Flags: recursesubdirs;  

[Icons]
Name: "{group}\PhotoFilmStrip"; Filename: "{app}\bin\PhotoFilmStrip.exe"
Name: "{group}\Help";           Filename: "{app}\doc\photofilmstrip\photofilmstrip.chm"
Name: "{group}\Uninstall";      Filename: "{app}\unins000.exe";       WorkingDir: "{app}";

[Run]
Filename: "{app}\bin\PhotoFilmStrip.exe"; Description: "Run PhotoFilmStrip"; Flags: postinstall skipifsilent nowait

