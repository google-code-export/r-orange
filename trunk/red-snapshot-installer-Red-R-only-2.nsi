; Include section
!include "MUI.nsh"

;General

  ;Name and file
  ;!define $SSVERSION "2010-04-20"
  Name "Red-R 1.7.Nightly-2010-04-20"
  OutFile "Red-R-1.7-Nightly-2010-04-20.exe"

;--------------------------------
; Defines
!define RVERSION "Red-R1.7.Snapshot-2010-04-18" ;                                           ;;; Change this when a new version is made
!define Red-RDIR C:\Python26\Lib\site-packages\redR1.5

;---------------------------------
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

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
	IfFileExists "$INSTDIR\${RVERSION}\*" ask_remove_old
    
    not_installed_before:
    MessageBox MB_OK "No Red-R data detected.  Please install the full version and not the code only version.$\r$\n$\r$\nYou may then install this version as an update." /SD IDOK IDOK done_install
    
    ask_remove_old:
		MessageBox MB_YESNOCANCEL "Another version of Red-R has been found on the computer.$\r$\nDo you want to keep the existing settings for canvas and widgets?$\r$\n$\r$\nYou can usually safely answer 'Yes'; in case of problems, re-run this installation." /SD IDYES IDYES dont_remove_settings IDNO remove_old_settings
			MessageBox MB_YESNO "Abort the installation?" IDNO ask_remove_old
				Quit

		remove_old_settings:
		RmDir /R "$0\red-r\settings"

	
    dont_remove_settings:
    
	SetOutPath $INSTDIR\${RVERSION}
	File /r /x .svn /x *.pyc /x settings /x R /x *.nsi "${Red-RDIR}\*"
   
    done_install:
    SectionEnd
