
[Setup]
AppName           = PhotoFilmStrip
AppPublisher      = Jens Göpfert
AppPublisherURL   = http://photostoryx.sourceforge.net
AppCopyright      = Copyright (C) 2008 Jens Göpfert
AppVerName        = {code:getAppVerName}
AppVersion        = {code:getAppVer}
;VersionInfoVersion= {code:getVerInfo}
DefaultDirName    = {code:getInstallDir}
DefaultGroupName  = PhotoFilmStrip
UninstallDisplayIcon={app}\bin\PhotoFilmStrip.exe
OutputDir=release
OutputBaseFilename = setup_photofilmstrip
LicenseFile       = copying
WizardSmallImageFile=res\icon\photofilmstrip.bmp
WizardImageFile=compiler:WizModernImage-IS.bmp
PrivilegesRequired=none
;compression=none

[Files]
Source: "dist\*";                   DestDir: "{app}";                     Flags: recursesubdirs;  
Source: "win32ExtBin\mplayer\*";    DestDir: "{app}\extBin\mplayer";      Flags: recursesubdirs;
Source: "version.info";                                                   Flags: dontcopy;

[Icons]
Name: "{group}\PhotoFilmStrip"; Filename: "{app}\bin\PhotoFilmStrip.exe"
Name: "{group}\Help";           Filename: "{app}\doc\photofilmstrip\photofilmstrip.chm"
Name: "{group}\Uninstall";      Filename: "{app}\unins000.exe";       WorkingDir: "{app}";

[Run]
Filename: "{app}\bin\PhotoFilmStrip.exe"; Description: "Run PhotoFilmStrip"; Flags: postinstall skipifsilent nowait

[Tasks]
Name: associate;   Description: "Associate with PFS Files";     Check: IsAdminLoggedOn;

[Registry]
Root: HKCR; Subkey: ".pfs"; ValueType: string; ValueName: ""; ValueData: "pfsfile"; Flags: uninsdeletevalue; Check: IsAdminLoggedOn; Tasks: associate
Root: HKCR; Subkey: "pfsfile"; ValueType: string; ValueName: ""; ValueData: "PhotoFilmStrip-Projekt"; Flags: uninsdeletekey; Check: IsAdminLoggedOn; Tasks: associate
Root: HKCR; Subkey: "pfsfile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\bin\PhotoFilmStrip.EXE,0"; Check: IsAdminLoggedOn; Tasks: associate
Root: HKCR; Subkey: "pfsfile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\bin\PhotoFilmStrip.EXE"" ""%1"""; Check: IsAdminLoggedOn; Tasks: associate

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

function getInstallDir(Default: String) :String;
begin
    if IsAdminLoggedOn() then
        result := ExpandConstant('{pf}\PhotoFilmStrip')
    else
        result := ExpandConstant('{userappdata}\PhotoFilmStrip')
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  case PageID of
    wpSelectTasks:
      Result := not IsAdminLoggedOn();
  else
    Result := False;
  end;
end;

