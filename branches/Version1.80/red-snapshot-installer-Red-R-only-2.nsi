; Include section
!include "MUI.nsh"

;General

  ;Name and file
  ;!define $SSVERSION "2010-04-20"
  Name "Red-R 1.7.Nightly"
  OutFile "Red-R-1.7-Nightly.exe"

;--------------------------------
; Defines
!define RVERSION "Red-R1.7.Snapshot" ;                                           ;;; Change this when a new version is made
!define Red-RDIR C:\Python26\Lib\site-packages\redR1.5-base

;---------------------------------
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

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
	File /r /x *.svn /x *.pyc /x Red-RPackages /x *.nsi "${Red-RDIR}\*"
   
   
   CreateDirectory "$SMPROGRAMS\Red-R\${RVERSION}"
    AccessControl::GrantOnFile "$SMPROGRAMS\Red-R" "(BU)" "FullAccess" ; required to give those with admin restrictions read write access to the files.
    
	CreateShortCut "$SMPROGRAMS\Red-R\${RVERSION}\Red-R Canvas ${RVERSION}.lnk" "$INSTDIR\${RVERSION}\canvas\red-RCanvas.pyw" "" $INSTDIR\${RVERSION}\canvas\icons\orange.ico 0
	CreateShortCut "$SMPROGRAMS\Red-R\${RVERSION}\Uninstall Red-R.lnk" "$INSTDIR\uninst ${RVERSION}.exe"

	;SetOutPath $INSTDIR\canvas
	CreateShortCut "$DESKTOP\Red-R Canvas ${RVERSION}.lnk" "$INSTDIR\${RVERSION}\canvas\red-RCanvas.pyw" "" $INSTDIR\${RVERSION}\canvas\icons\orange.ico 0
	;CreateShortCut "$SMPROGRAMS\Red-R\Red-R Canvas.lnk" "$INSTDIR\canvas\red-RCanvas.pyw" "" $INSTDIR\canvas\icons\orange.ico 0

	WriteRegStr SHELL_CONTEXT "SOFTWARE\Python\PythonCore\2.6\PythonPath\Red-R\${RVERSION}" "" "$INSTDIR\${RVERSION};$INSTDIR\${RVERSION}\OrangeWidgets;$INSTDIR\${RVERSION}\canvas"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${RVERSION}" "DisplayName" "Red-R (remove only)"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${RVERSION}" "UninstallString" '"$INSTDIR\uninst ${RVERSION}.exe"'

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
    WriteRegStr HKEY_CLASSES_ROOT ".rrp" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${RVERSION}\canvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$PythonDir\pythonw.exe $INSTDIR\${RVERSION}\canvas\red-RCanvas.pyw "%1"';name is appended into the sys.argv variables for opening by Red-R
    WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\RedRDir" "" "$INSTDIR"
    
    WriteUninstaller "$INSTDIR\uninst ${RVERSION}.exe"
    
    done_install:
SectionEnd

Section Uninstall
	MessageBox MB_YESNO "Are you sure you want to remove Red-R?$\r$\n$\r$\nThis won't remove any 3rd party software possibly installed with Red-R, such as Python or Qt,$\r$\n$\r$\nbut make sure you have not left any of your files in Red-R's directories!" /SD IDYES IDNO abort
	
	${If} $AdminInstall = 0
	    SetShellVarContext all
	${Else}
	    SetShellVarContext current	   
	${Endif}
    RmDir /R /REBOOTOK "$INSTDIR\${RVERSION}"
	RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R\${RVERSION}"

    MessageBox MB_YESNO "Would you like to remove your Red-R settings?" /SD IDYES IDNO remove_keys
    
	ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
	StrCmp $0 "" 0 +2
	  ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
	StrCmp $0 "" +2 0
	  RmDir /R /REBOOTOK "$0\red-r\settings"
	
    remove_keys:

    DeleteRegKey HKCU "SOFTWARE\Red-R\${RVERSION}"
    DeleteRegKey HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${RVERSION}"
	
	Delete "$DESKTOP\Red-R Canvas ${RVERSION}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    MessageBox MB_YESNO "Would you like to remove all previous versions of Red-R?$\r$\nRemoves the entire Red-R directory." /SD IDYES IDNO removed_OK
    
    RmDir /R /REBOOTOK "$INSTDIR"
    RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R"
    
    removed_OK:
	MessageBox MB_OK "Red-R ${RVERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine.$\r$\n$\r$\nIf you want to use an older version of Red-R you should reinstall that version." /SD IDOK
   abort:
SectionEnd