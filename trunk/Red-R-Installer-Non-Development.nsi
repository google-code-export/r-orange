; need the nsisdt and AccessControl plugins
;--------------------------------
; Defines
!define Red-RDIR C:\Users\anup\Documents\red\develop\red
!define SubWCRev "C:\Program Files\TortoiseSVN\bin\SubWCRev.exe"
!define LICENSE ${Red-RDIR}\licence2.txt 
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
; creates variables ${REDRVERSION}, ${DATE}, ${SVNVERSION}
!include "${Red-RDIR}\version.txt"

Name "${REDRVERSION}"

;---------------------------------
; General
  OutFile "C:\Users\anup\Documents\red\develop\installer\${REDRVERSION}-${DATE}.r${SVNVERSION}.exe"
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

	
    SetOutPath "$INSTDIR\${REDRVERSION}"
	File ${Red-RDIR}\version.txt

	SetOutPath "$INSTDIR\${REDRVERSION}\bin"
    File /r /x .svn ${BIN}\*
    
    SetOutPath "$INSTDIR\${REDRVERSION}\canvas\icons"
	File /r /x .svn /x *.pyc /x .nsi ${CANVASICONS}\*
    
    SetOutPath "$INSTDIR\${REDRVERSION}\libraries"
	File /r /x .svn /x *.pyc /x .nsi ${LIBRARIES}\*

    SetOutPath "$INSTDIR\${REDRVERSION}\tagsSystem"
	File /r /x .svn /x *.pyc /x .nsi ${TAGS}\*

    SetOutPath "$INSTDIR\${REDRVERSION}\Examples"
	File /r /x .svn /x *.pyc /x .nsi ${EXAMPLES}\*


    
    IfFileExists $INSTDIR\R\README.${RVER}.* has_R

        SetOutPath $INSTDIR\R
        File /r /x .svn ${RDIRECTORY}\*
        ; grant access to modify the files in this directory
        AccessControl::GrantOnFile "$INSTDIR\R\library" "(BU)" "FullAccess" 
        AccessControl::GrantOnFile "$INSTDIR\R\doc" "(BU)" "FullAccess" 

    has_R:

;------------------------
; Create the shortcuts    
	CreateDirectory "$SMPROGRAMS\Red-R\${REDRVERSION}"
	CreateShortCut "$SMPROGRAMS\Red-R\${REDRVERSION}\Red-R Canvas.lnk" "$INSTDIR\${REDRVERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${REDRVERSION}\canvas\icons\orange.ico" 0
    CreateShortCut "$SMPROGRAMS\Red-R\${REDRVERSION}\Uninstall Red-R.lnk" "$INSTDIR\${REDRVERSION}\uninst ${REDRVERSION}.exe"

	CreateShortCut "$DESKTOP\Red-R Canvas ${REDRVERSION}.lnk" "$INSTDIR\${REDRVERSION}\bin\red-RCanvas.exe" "" "$INSTDIR\${REDRVERSION}\canvas\icons\orange.ico" 0
	
;-------------------------
; Write the registry settings
	; WriteRegStr SHELL_CONTEXT "SOFTWARE\Red-R\${REDRVERSION}" "" "$INSTDIR\${REDRVERSION};$INSTDIR\${REDRVERSION}\OrangeWidgets$INSTDIR\${REDRVERSION}\OrangeCanvas"
	
;-------------------------
; Write the registry settings Uninstall
    
    WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REDRVERSION}" "DisplayName" "${REDRVERSION}"
    
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REDRVERSION}" "UninstallString" '"$INSTDIR\${REDRVERSION}\uninst ${REDRVERSION}.exe"'
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REDRVERSION}" "Publisher" "Red-R Core Development Team"
    

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${REDRVERSION}\canvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$INSTDIR\${REDRVERSION}\bin\red-RCanvas.exe "%1"';name is appended into the sys.argv variables for opening by Red-R
    
	WriteUninstaller "$INSTDIR\${REDRVERSION}\uninst ${REDRVERSION}.exe"

SectionEnd

Section Uninstall
    MessageBox MB_YESNO "Are you sure you want to remove Red-R?" /SD IDYES IDNO end
	
    Delete "$INSTDIR\uninst ${REDRVERSION}.exe"
    
    RmDir /r /REBOOTOK "$INSTDIR"
	
    RmDir /r /REBOOTOK "$SMPROGRAMS\Red-R\${REDRVERSION}"
    
    MessageBox MB_YESNO "Would you like to remove your Red-R ${REDRVERSION} settings?" /SD IDYES IDNO remove_keys
    
        ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
        StrCmp $0 "" 0 +2
          ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
        StrCmp $0 "" +2 0
          RmDir /r /REBOOTOK "$0\red-r\settings"
	
    remove_keys:

    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Red-R\${REDRVERSION}"
    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${REDRVERSION}"
	
	Delete "$DESKTOP\Red-R Canvas ${REDRVERSION}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    ; IfErrors jumpto_iferror 
        IfRebootFlag jumpto_IfRebootFlag jumpto_IfNoRebootFlag
        jumpto_IfRebootFlag:
            MessageBox MB_OK "Red-R ${REDRVERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine." /SD IDOK
            Goto end
        jumpto_IfNoRebootFlag:
            MessageBox MB_OK "Red-R ${REDRVERSION} has been successfully removed from your system." /SD IDOK
            Goto end
        
    ; jumpto_iferror:
        ; MessageBox MB_OK "Red-R ${REDRVERSION} Error!" /SD IDOK

   end:
SectionEnd
