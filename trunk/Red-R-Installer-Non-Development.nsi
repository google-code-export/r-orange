; Include section
!include "MUI.nsh"


;General
  Name "Red-R 1.7"
  OutFile "C:\Users\anup\Documents\red\develop\installer\Red-R-non-developer-Snapshot-10.04.26.exe"

  ;Name and file

;--------------------------------
; Defines
!define Red-RDIR C:\Users\anup\Documents\red\develop\red

!define Red-RLICENSE ${Red-RDIR}\licence2.txt 
!define Red-RDIR_bin ${Red-RDIR}\dist
!define Red-RDIR_canvas ${Red-RDIR}\canvas\icons
!define Red-RDIR_widgets ${Red-RDIR}\OrangeWidgets
!define Red-RDIR_tags ${Red-RDIR}\tagsSystem
!define RDIRECTORY C:\Users\anup\Documents\red\develop\installer\R ;;;; The directory of a blank R so that we don't have to deal with licence terms of R


!define RVER "R"
!define RVERSION Red-R1.7 ;;;; Change this when a new version is made

;---------------------------------
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;---------------------------------

; Var StartMenuFolder
; Var AdminInstall

!define SHELLFOLDERS \
  "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
!insertmacro MUI_PAGE_LICENSE ${Red-RLICENSE}
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
  
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; languages
!insertmacro MUI_LANGUAGE "English"
Section Uninstall
	MessageBox MB_YESNO "Are you sure you want to remove Red-R?" /SD IDYES IDNO abort
	
	; ${If} $AdminInstall = 0
	    ; SetShellVarContext all
	; ${Else}
	    ; SetShellVarContext current	   
	; ${Endif}
    RmDir /R /REBOOTOK "$INSTDIR\${RVERSION}"
	RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R\${RVERSION}"

    MessageBox MB_YESNO "Would you like to remove your Red-R ${RVERSION} settings?" /SD IDYES IDNO remove_keys
    
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

	MessageBox MB_OK "Red-R ${RVERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine.$\r$\n$\r$\nIf you want to use an older version of Red-R you should reinstall that version." /SD IDOK
   abort:
SectionEnd

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

	; StrCpy $INSTDIR  "C:\Program Files\Red-R\${RVERSION}"
    ; AccessControl::GrantOnFile "$INSTDIR" "(BU)" "FullAccess" ; required to give those with admin restrictions read write access to the files.
	SetOutPath $INSTDIR\${RVERSION}\bin
    File /r /x .svn ${Red-RDIR_bin}\*
    
    SetOutPath $INSTDIR\${RVERSION}\canvas\icons
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_canvas}\*
    
    SetOutPath $INSTDIR\${RVERSION}\OrangeWidgets
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_widgets}\*

    SetOutPath $INSTDIR\${RVERSION}\tagsSystem
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_tags}\*

    
    IfFileExists $INSTDIR\R\README.${RVER}.* has_R

    SetOutPath $INSTDIR\R
    File /r /x .svn ${RDIRECTORY}\*
    ; grant access to modify the files in this directory
    AccessControl::GrantOnFile "$INSTDIR\R\library" "(BU)" "FullAccess" 
    AccessControl::GrantOnFile "$INSTDIR\R\doc" "(BU)" "FullAccess" 

    has_R:

;------------------------
; Create the shortcuts    
	CreateDirectory "$SMPROGRAMS\Red-R\${RVERSION}"
	CreateShortCut "$SMPROGRAMS\Red-R\${RVERSION}\Red-R Canvas.lnk" "$INSTDIR\${RVERSION}\bin\red-RCanvas.exe" "" $INSTDIR\${RVERSION}\OrangeCanvas\icons\orange.ico 0
    CreateShortCut "$SMPROGRAMS\Red-R\${RVERSION}\Uninstall Red-R.lnk" "$INSTDIR\${RVERSION}\uninst ${RVERSION}.exe"

	CreateShortCut "$DESKTOP\Red-R Canvas ${RVERSION}.lnk" "$INSTDIR\${RVERSION}\bin\red-RCanvas.exe" "" $INSTDIR\${RVERSION}\OrangeCanvas\icons\orange.ico 0
	
;-------------------------
; Write the registry settings
	WriteRegStr SHELL_CONTEXT "SOFTWARE\Red-R\${RVERSION}" "" "$INSTDIR\${RVERSION};$INSTDIR\${RVERSION}\OrangeWidgets$INSTDIR\${RVERSION}\OrangeCanvas"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${RVERSION}" "DisplayName" "Red-R (remove only)"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${RVERSION}" "UninstallString" '"$INSTDIR\${RVERSION}\uninst ${RVERSION}.exe"'

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${RVERSION}\OrangeCanvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$INSTDIR\${RVERSION}\bin\red-RCanvas.exe "%1"';name is appended into the sys.argv variables for opening by Red-R
    
	WriteUninstaller "$INSTDIR\${RVERSION}\uninst ${RVERSION}.exe"

SectionEnd

