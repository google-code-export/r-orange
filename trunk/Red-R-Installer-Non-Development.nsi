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
; creates variables ${NAME}-${VERSION}, ${DATE}, ${SVNVERSION}
!include "${Red-RDIR}\version.txt"

Name "${NAME}-${VERSION}"

;---------------------------------
; General
  OutFile "C:\Users\anup\Documents\red\develop\installer\${NAME}-${VERSION}-${DATE}.r${SVNVERSION}.exe"
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

	
    SetOutPath "$INSTDIR\${NAME}-${VERSION}"
	File ${Red-RDIR}\version.txt

	SetOutPath "$INSTDIR\${NAME}-${VERSION}\bin"
    File /r /x .svn ${BIN}\*
    
    SetOutPath "$INSTDIR\${NAME}-${VERSION}\canvas\icons"
	File /r /x .svn /x *.pyc /x .nsi ${CANVASICONS}\*
    
    SetOutPath "$INSTDIR\${NAME}-${VERSION}\libraries\base"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\base\*
    
    SetOutPath "$INSTDIR\${NAME}-${VERSION}\libraries\plotting"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\plotting\*
    
    SetOutPath "$INSTDIR\${NAME}-${VERSION}\libraries\stats"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\stats\*

    SetOutPath "$INSTDIR\${NAME}-${VERSION}\Examples"
	File /r /x .svn /x *.pyc /x .nsi ${EXAMPLES}\*


    AccessControl::GrantOnFile "$INSTDIR\${NAME}-${VERSION}" "(BU)" "FullAccess" 
    
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
	CreateDirectory "$SMPROGRAMS\Red-R\${NAME}-${VERSION}"
	CreateShortCut "$SMPROGRAMS\Red-R\${NAME}-${VERSION}\Red-R Canvas.lnk" "$INSTDIR\${NAME}-${VERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${NAME}-${VERSION}\canvas\icons\orange.ico" 0
    CreateShortCut "$SMPROGRAMS\Red-R\${NAME}-${VERSION}\Uninstall Red-R.lnk" "$INSTDIR\${NAME}-${VERSION}\uninst ${NAME}-${VERSION}.exe"

	CreateShortCut "$DESKTOP\Red-R Canvas ${NAME}-${VERSION}.lnk" "$INSTDIR\${NAME}-${VERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${NAME}-${VERSION}\canvas\icons\orange.ico" 0
	
;-------------------------
; Write the registry settings
	; WriteRegStr SHELL_CONTEXT "SOFTWARE\Red-R\${NAME}-${VERSION}" "" "$INSTDIR\${NAME}-${VERSION};$INSTDIR\${NAME}-${VERSION}\OrangeWidgets$INSTDIR\${NAME}-${VERSION}\OrangeCanvas"
	
;-------------------------
; Write the registry settings Uninstall
    
    WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${VERSION}" "DisplayName" "${NAME}-${VERSION}"
    
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${VERSION}" "UninstallString" '"$INSTDIR\${NAME}-${VERSION}\uninst ${NAME}-${VERSION}.exe"'
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${VERSION}" "Publisher" "Red-R Core Development Team"
    

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT ".rrp" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT ".rrts" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${NAME}-${VERSION}\canvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$INSTDIR\${NAME}-${VERSION}\bin\red-RCanvas.exe "%1"';name is appended into the sys.argv variables for opening by Red-R
    
	WriteUninstaller "$INSTDIR\${NAME}-${VERSION}\uninst ${NAME}-${VERSION}.exe"

SectionEnd

Section Uninstall
    MessageBox MB_YESNO "Are you sure you want to remove Red-R?" /SD IDYES IDNO end
	
    Delete "$INSTDIR\uninst ${NAME}-${VERSION}.exe"
    
    RmDir /r /REBOOTOK "$INSTDIR"
	
    RmDir /r /REBOOTOK "$SMPROGRAMS\Red-R\${NAME}-${VERSION}"
    
    MessageBox MB_YESNO "Would you like to remove your Red-R ${NAME}-${VERSION} settings?" /SD IDYES IDNO remove_keys
    
        ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
        StrCmp $0 "" 0 +2
          ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
        StrCmp $0 "" +2 0
          RmDir /r /REBOOTOK "$0\red-r\settings"
	
    remove_keys:

    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Red-R\${NAME}-${VERSION}"
    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}-${VERSION}"
	
	Delete "$DESKTOP\Red-R Canvas ${NAME}-${VERSION}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    ; IfErrors jumpto_iferror 
        IfRebootFlag jumpto_IfRebootFlag jumpto_IfNoRebootFlag
        jumpto_IfRebootFlag:
            MessageBox MB_OK "Red-R ${NAME}-${VERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine." /SD IDOK
            Goto end
        jumpto_IfNoRebootFlag:
            MessageBox MB_OK "Red-R ${NAME}-${VERSION} has been successfully removed from your system." /SD IDOK
            Goto end
        
    ; jumpto_iferror:
        ; MessageBox MB_OK "Red-R ${NAME}-${VERSION} Error!" /SD IDOK

   end:
SectionEnd
