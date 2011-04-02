
[Setup]
AppName           = PhotoFilmStrip
AppPublisher      = Jens Göpfert
AppPublisherURL   = http://www.photofilmstrip.org
AppCopyright      = Copyright (C) 2008 Jens Göpfert
AppVerName        = {code:getAppVerName}
AppVersion        = {code:getAppVer}
;VersionInfoVersion= {code:getVerInfo}
DefaultDirName    = {code:getInstallDir}
DefaultGroupName  = PhotoFilmStrip
UninstallDisplayIcon={app}\bin\PhotoFilmStrip.exe
OutputDir=..\dist
OutputBaseFilename = setup_photofilmstrip
LicenseFile       = ..\copying
WizardSmallImageFile=..\res\icon\photofilmstrip.bmp
WizardImageFile=compiler:WizModernImage-IS.bmp
PrivilegesRequired=none
compression=none

[Files]
Source: "..\build\dist\*";             DestDir: "{app}"; Flags: recursesubdirs;
Source: "..\version.info";                               Flags: dontcopy;
Source: "..\windows\vcredist_x86.exe"; DestDir: "{tmp}";

[Icons]
Name: "{group}\PhotoFilmStrip"; Filename: "{app}\bin\PhotoFilmStrip.exe"
Name: "{group}\Help";           Filename: "{app}\share\doc\photofilmstrip\photofilmstrip.chm"
Name: "{group}\Uninstall";      Filename: "{app}\unins000.exe";       WorkingDir: "{app}";

[Run]
Filename: "{tmp}\vcredist_x86.exe"; WorkingDir: {tmp}; Parameters: "/q /l {tmp}\vcredist.log"; StatusMsg: Microsoft Visual C++ 2008 Redistributable Setup...; Flags: waituntilterminated; Tasks: vcredist;
Filename: "{app}\bin\PhotoFilmStrip.exe"; Description: "Run PhotoFilmStrip"; Flags: postinstall skipifsilent nowait;

[Tasks]
Name: associate;   Description: "Associate with PFS Files";                  Check: IsAdminLoggedOn;
Name: vcredist;    Description: "Microsoft Visual C++ 2008 Redistributable"; Check: VCRedistCheck and IsAdminLoggedOn;

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

function VCRedistCheck(): Boolean;
begin
  if RegValueExists(HKEY_LOCAL_MACHINE,
                    'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}',
                    'Version') then
      result := False
  else
      result := True
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if PageID=wpSelectTasks then
  begin
      if not VCRedistCheck() and not IsAdminLoggedOn() then
        MsgBox('Microsoft Visual C++ 2008 Redistributable package is needed, but administrative privileges are required to install it. Please make sure to install it yourself before running the application.', mbInformation, MB_OK)
      result := not IsAdminLoggedOn();
  end else
    result := False;
end;

