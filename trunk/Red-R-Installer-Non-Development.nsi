; need the nsisdt and AccessControl plugins
;--------------------------------
; Defines
!define Red-RDIR C:\Users\anup\Documents\red\develop\red
!define SubWCRev "C:\Program Files\TortoiseSVN\bin\SubWCRev.exe"
!define LICENSE ${Red-RDIR}\licence.txt 
!define BIN ${Red-RDIR}\dist
!define CANVASICONS ${Red-RDIR}\canvas\icons
!define LIBRARIES ${Red-RDIR}\libraries
!define TAGS ${Red-RDIR}\tagsSystem
!define EXAMPLES ${Red-RDIR}\Examples
!define RDIRECTORY C:\Users\anup\Documents\red\develop\installer\R ;;;; The directory of a blank R so that we don't have to deal with licence terms of R
!define RVER "R-2.9.1"


;---------------------------------
; Include section

!include "MUI.nsh"
!system '"${SubWCRev}" "${Red-RDIR}" "${Red-RDIR}\version.tpl" "${Red-RDIR}\version.txt"'

; get revision number and date
; creates variables ${NAME}-${REDRVERSION}, ${DATE}, ${SVNVERSION}
!include "${Red-RDIR}\version.txt"

Name "${NAME}-${REDRVERSION}"

;---------------------------------
; General
  OutFile "C:\Users\anup\Documents\red\develop\installer\${NAME}-${REDRVERSION}-${DATE}.r${SVNVERSION}.exe"
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

  
;---------------------------------
!define SHELLFOLDERS \
  "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
!insertmacro MUI_PAGE_LICENSE ${LICENSE}
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
  
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; languages
!insertmacro MUI_LANGUAGE "English"

Section "" ;this is the section that will install Red-R and all of it's files
    ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
	StrCmp $0 "" 0 +2
	ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
	StrCmp $0 "" not_installed_before 0

    ; if another version was installed should we remove the data set by orngEnviron before install?
	IfFileExists "$0\red-r\settings" 0 not_installed_before
		ask_remove_old:
		MessageBox MB_YESNOCANCEL "Another version of Red-R has been found on the computer.$\r$\nDo you want to keep the existing settings for canvas and widgets?$\r$\n$\r$\nYou can usually safely answer 'Yes'; in case of problems, re-run this installation." /SD IDYES IDYES not_installed_before IDNO remove_old_settings
			MessageBox MB_YESNO "Abort the installation?" IDNO ask_remove_old
				Quit

		remove_old_settings:
		
    ; end removal of settings
	not_installed_before:

	
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}"
	File ${Red-RDIR}\version.txt

	SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\*
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\canvas\icons"
	File /r /x .svn /x *.pyc /x .nsi ${CANVASICONS}\*
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\libraries\base"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\base\*
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\libraries\plotting"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\plotting\*
    
    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\libraries\stats"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\stats\*

    SetOutPath "$INSTDIR\${NAME}-${REDRVERSION}\Examples"
	File /r /x .svn /x *.pyc /x .nsi ${EXAMPLES}\*


    AccessControl::GrantOnFile "$INSTDIR\${NAME}-${REDRVERSION}" "(BU)" "FullAccess" 
    
    IfFileExists $INSTDIR\R\README.${RVER}.* has_R
        SetOutPath $INSTDIR\R
        File /r /x .svn ${RDIRECTORY}\*
        ; grant access to modify the files in this directory
        AccessControl::GrantOnFile "$INSTDIR\R\library" "(BU)" "FullAccess" 
        AccessControl::GrantOnFile "$INSTDIR\R\doc" "(BU)" "FullAccess" 

    has_R:

;------------------------
; Create the shortcuts    
    
    CreateDirectory "$DOCUMENTS\Red-R"
    CreateDirectory "$DOCUMENTS\Red-R\Templates"
    CreateDirectory "$DOCUMENTS\Red-R\Schemas"
	CreateDirectory "$SMPROGRAMS\Red-R\${NAME}-${REDRVERSION}"
	CreateShortCut "$SMPROGRAMS\Red-R\${NAME}-${REDRVERSION}\Red-R Canvas.lnk" "$INSTDIR\${NAME}-${REDRVERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${NAME}-${REDRVERSION}\canvas\icons\orange.ico" 0
    CreateShortCut "$SMPROGRAMS\Red-R\${NAME}-${REDRVERSION}\Uninstall Red-R.lnk" "$INSTDIR\uninst ${NAME}-${REDRVERSION}.exe"

	CreateShortCut "$DESKTOP\Red-R Canvas ${NAME}-${REDRVERSION}.lnk" "$INSTDIR\${NAME}-${REDRVERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${NAME}-${REDRVERSION}\canvas\icons\orange.ico" 0
	
;-------------------------
; Write the registry settings
	; WriteRegStr SHELL_CONTEXT "SOFTWARE\Red-R\${NAME}-${REDRVERSION}" "" "$INSTDIR\${NAME}-${REDRVERSION};$INSTDIR\${NAME}-${REDRVERSION}\OrangeWidgets$INSTDIR\${NAME}-${REDRVERSION}\OrangeCanvas"
	
;-------------------------
; Write the registry settings Uninstall
    
    WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${REDRVERSION}" "DisplayName" "${NAME}-${REDRVERSION}"
    
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${REDRVERSION}" "UninstallString" '"$INSTDIR\${NAME}-${REDRVERSION}\uninst ${NAME}-${REDRVERSION}.exe"'
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${REDRVERSION}" "Publisher" "Red-R Core Development Team"
    

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT ".rrp" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT ".rrts" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${NAME}-${REDRVERSION}\canvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$INSTDIR\${NAME}-${REDRVERSION}\bin\red-RCanvas.exe "%1"';name is appended into the sys.argv variables for opening by Red-R
    
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
    
    MessageBox MB_YESNO "Would you like to remove all previous versions of Red-R?$\r$\nRemoves the entire Red-R directory." /SD IDYES IDNO removed_OK
    
    RmDir /R /REBOOTOK "$INSTDIR"
    RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R"
    
    removed_OK:

    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Red-R\${NAME}-${REDRVERSION}"
    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${REDRVERSION}"
	
	Delete "$DESKTOP\Red-R Canvas ${NAME}-${REDRVERSION}.lnk"

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
