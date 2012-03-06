; need the nsisdt and AccessControl plugins
;--------------------------------
; Defines

!define SubWCRev "C:\Program Files\TortoiseSVN\bin\SubWCRev.exe"
!define LICENSE ${Red-RDIR}\licence.txt 
!define BIN ${Red-RDIR}\dist
!define CANVASICONS ${Red-RDIR}\canvas\icons
!define LIBRARIES ${Red-RDIR}\libraries
!define EXAMPLES ${Red-RDIR}\Examples
!define SHELLFOLDERS "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"


;---------------------------------
; Include section

!include "MUI.nsh"
!system '"${SubWCRev}" "${Red-RDIR}" "${Red-RDIR}/version.tpl" "${Red-RDIR}/version.txt"'
!system 'echo !define NAME "Red-R" >> "${Red-RDIR}\version.txt"'
!system 'echo !define REDRVERSION "${REDRVERSION1}" >> "${Red-RDIR}\version.txt"'
!system 'echo !define TYPE "compiled" >> "${Red-RDIR}\version.txt"'
!system 'echo !define RVERSION "${RVER}" >> "${Red-RDIR}\version.txt"'

; get revision number and date
; creates variables ${NAME}-${REDRVERSION}, ${DATE}, ${SVNVERSION}
!include "${Red-RDIR}\version.txt"

Name "${NAME}-${REDRVERSION}"

;---------------------------------
; General
  OutFile "${OUTPUTDIR}\${NAME}-${REDRVERSION}-Update-${DATE}.r${SVNVERSION}.exe"
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

  
;---------------------------------
!insertmacro MUI_PAGE_LICENSE ${LICENSE}
; !insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
  
; !insertmacro MUI_UNPAGE_CONFIRM
; !insertmacro MUI_UNPAGE_INSTFILES

; languages
!insertmacro MUI_LANGUAGE "English"

Section "" ;this is the section that will install Red-R and all of it's files

    checkRunning:
    FindWindow $0 "" "Red-R Canvas Version ${REDRVERSION}"
    StrCmp $0 0 notRunning
        MessageBox MB_OK|MB_RETRYCANCEL|MB_ICONEXCLAMATION "Red-R is running. Please close it first." /SD IDOK IDRETRY checkRunning
        Abort
    notRunning:
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}"
	File ${Red-RDIR}\version.txt
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}"
	File ${LICENSE}
    
    
    Delete "$INSTDIR\${NAME}-${REDRVERSION}\*.py"	
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\*.py

    Delete "$INSTDIR\${NAME}-${REDRVERSION}\red-RCanvas.exe"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\red-RCanvas.exe

    Delete "$INSTDIR\${NAME}-${REDRVERSION}\redrrpy._conversion.pyd"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\redrrpy._conversion.pyd
    
    RmDir /r "$INSTDIR\${NAME}-${REDRVERSION}\bin\redrrpy"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\redrrpy
    
    Delete "$INSTDIR\${NAME}-${REDRVERSION}\rpy3.rinterface.rinterface.pyd"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\rpy3.rinterface.rinterface.pyd

    RmDir /r "$INSTDIR\${NAME}-${REDRVERSION}\bin\rpy3"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\rpy3
    
    RmDir /r "$INSTDIR\${NAME}-${REDRVERSION}\canvas"
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\canvas\icons"
	File /r /x .svn /x *.pyc /x .nsi ${CANVASICONS}\*
    
    RmDir /r "$INSTDIR\${NAME}-${REDRVERSION}\libraries\base"    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\libraries\base"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\base\*


    AccessControl::GrantOnFile "$INSTDIR\${NAME}-${REDRVERSION}" "(BU)" "FullAccess" 
    AccessControl::GrantOnFile "$INSTDIR\R" "(BU)" "FullAccess" 
       
	WriteUninstaller "$INSTDIR\uninst ${NAME}-${REDRVERSION}.exe"

SectionEnd

Section Uninstall
    MessageBox MB_YESNO "Are you sure you want to remove Red-R?" /SD IDYES IDNO end
	
    Delete "$INSTDIR\uninst ${NAME}-${REDRVERSION}.exe"
    
    RmDir /r /REBOOTOK "$INSTDIR\${NAME}-${REDRVERSION}"
	
    RmDir /r /REBOOTOK "$SMPROGRAMS\Red-R\${NAME}-${REDRVERSION}"
    
    MessageBox MB_YESNO "Would you like to remove your Red-R ${NAME}-${REDRVERSION} settings?" /SD IDYES IDNO remove_keys
    
        ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
        StrCmp $0 "" 0 +2
          ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
        StrCmp $0 "" +2 0
          RmDir /r /REBOOTOK "$0\red-r"
	
    remove_keys:
    
    MessageBox MB_YESNO "Would you like to remove all previous versions of Red-R?$\r$\nThis will remove the entire Red-R directory." /SD IDYES IDNO removed_OK
    
    RmDir /R /REBOOTOK "$INSTDIR"
    RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R"
    
    removed_OK:

    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Red-R\${NAME}-${REDRVERSION}"
    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${REDRVERSION}"
	
	Delete "$DESKTOP\${NAME}-${REDRVERSION}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    ; IfErrors jumpto_iferror 
        IfRebootFlag jumpto_IfRebootFlag jumpto_IfNoRebootFlag
        jumpto_IfRebootFlag:
            MessageBox MB_OK "Red-R ${NAME}-${REDRVERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine." /SD IDOK
            Goto end
        jumpto_IfNoRebootFlag:
            MessageBox MB_OK "Red-R ${NAME}-${REDRVERSION} has been successfully removed from your system." /SD IDOK
            Goto end
        
    ; jumpto_iferror:
        ; MessageBox MB_OK "Red-R ${NAME}-${REDRVERSION} Error!" /SD IDOK

   end:
SectionEnd
