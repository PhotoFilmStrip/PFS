
[Setup]
AppName           = PhotoFilmStrip
AppVerName        = PhotoFilmStrip 0.95
AppPublisher      = Jens Göpfert
AppPublisherURL   = http://photostoryx.sourceforge.net
AppVersion        = 0.95
AppCopyright      = Copyright (C) 2008 Jens Göpfert
DefaultDirName    = {pf}\PhotoFilmStrip-0.95
DefaultGroupName  = PhotoFilmStrip
UninstallDisplayIcon={app}\bin\PhotoFilmStrip.exe
OutputDir=release
OutputBaseFilename = setup_photofilmstrip-0.95
LicenseFile       = copying
VersionInfoVersion        = 0.9.5.0
WizardSmallImageFile=res\icon\photofilmstrip.bmp
WizardImageFile=compiler:WizModernImage-IS.bmp
compression=none

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "program";    Description: "Program Files"; Types: full compact custom; Flags: fixed
Name: "help";       Description: "Help File";     Types: full compact
Name: "mjpegtools"; Description: "MJPEG-Tools";   Types: full
Name: "imagemagick";Description: "ImageMagick";   Types: full; ExtraDiskSpaceRequired: 41402474
Name: "mplayer";    Description: "MPlayer";       Types: full

[Files]
Source: "dist\*";              DestDir: "{app}";                     Flags: recursesubdirs;  Components: program
Source: "winbin\mjpegtools\*"; DestDir: "{app}\extBin\mjpegtools";   Flags: recursesubdirs;  Components: mjpegtools
Source: "winbin\mplayer\*";    DestDir: "{app}\extBin\mplayer";      Flags: recursesubdirs;  Components: mplayer
Source: "doc\*";               DestDir: "{app}\doc";                                         Components: help
Source: "winbin\ImageMagick-6.4.5-5-Q8-windows-dll.exe";             DestDir: "{tmp}";

[Icons]
Name: "{group}\PhotoFilmStrip"; Filename: "{app}\bin\PhotoFilmStrip.exe"
Name: "{group}\Help";           Filename: "{app}\doc\index.html"
Name: "{group}\Uninstall";      Filename: "{app}\unins000.exe";       WorkingDir: "{app}";

[Run]
Filename: "{tmp}\ImageMagick-6.4.5-5-Q8-windows-dll.exe"; Description: "installing ImageMagick..."; Flags: shellexec waituntilterminated; Components: imagemagick
Filename: "{app}\bin\PhotoFilmStrip.exe"; Description: "Run PhotoFilmStrip"; Flags: postinstall skipifsilent nowait

