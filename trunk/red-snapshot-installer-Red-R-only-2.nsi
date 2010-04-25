; Include section
!include "MUI.nsh"

;General

  ;Name and file
  ;!define $SSVERSION "2010-04-20"
  Name "Red-R 1.7.Nightly"
  OutFile "Red-R-1.7-Nightly.exe"

;--------------------------------
; Defines
!define RVERSION "Red-R1.7.Snapshot-ND" ;                                           ;;; Change this when a new version is made
!define Red-RDIR C:\Python26\Lib\site-packages\redR1.5

;---------------------------------
  ;Default installation folder
  ;InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

  ; install to the last RedRDir
  InstallDirRegKey HKCU "Red R Canvas\RedRDir" ""
  
  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;---------------------------------

Var PythonDir
Var AdminInstall

!define SHELLFOLDERS \
  "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
!insertmacro MUI_PAGE_LICENSE "C:\Python26\Lib\site-packages\redR1.5\licence2.txt "
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; languages
!insertmacro MUI_LANGUAGE "English"

Section "" ;this is the section that will install Red-R and all of it's files
	IfFileExists "$INSTDIR\R\*" has_R
    
    MessageBox MB_OK "No Red-R data detected.  Please install the full version and not the code only version.$\r$\n$\r$\nYou may then install this version as an update." /SD IDOK IDOK done_install
    
    has_R:
    
	SetOutPath $INSTDIR\${RVERSION}
	File /r /x .svn /x *.pyc /x settings /x R /x *.nsi "${Red-RDIR}\*"
   
    done_install:
    SectionEnd
