
[Setup]
AppName           = PhotoFilmStrip
AppPublisher      = Jens Göpfert
AppPublisherURL   = http://photostoryx.sourceforge.net
AppCopyright      = Copyright (C) 2008 Jens Göpfert
AppVerName        = {code:getAppVerName}
AppVersion        = {code:getAppVer}
;VersionInfoVersion= {code:getVerInfo}
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
Source: "version.info";                                                   Flags: dontcopy;

[Icons]
Name: "{group}\PhotoFilmStrip"; Filename: "{app}\bin\PhotoFilmStrip.exe"
Name: "{group}\Help";           Filename: "{app}\doc\photofilmstrip\photofilmstrip.chm"
Name: "{group}\Uninstall";      Filename: "{app}\unins000.exe";       WorkingDir: "{app}";

[Run]
Filename: "{app}\bin\PhotoFilmStrip.exe"; Description: "Run PhotoFilmStrip"; Flags: postinstall skipifsilent nowait


[Code]
function getAppVer(Default: String) :String;
var tmp, s: String;
begin
    ExtractTemporaryFile('version.info');
    tmp := ExpandConstant('{tmp}\version.info');
    if LoadStringFromFile(tmp, s) then
        result := s
    else
        result := ''
end;

function getAppVerName(Default: String) :String;
begin
    result := ExpandConstant('PhotoFilmStrip ' + getAppVer(''))
end;
