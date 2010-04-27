; Include section
!include "MUI.nsh"

;General
  Name "Red-R 1.7"
  OutFile "C:\Users\anup\Documents\red\develop\installer\Red-R-non-developer-Snapshot-10.04.27.exe"

  ;Name and file

;--------------------------------
; Defines
!define Red-RDIR C:\Users\anup\Documents\red\develop\red

!define Red-RLICENSE ${Red-RDIR}\licence2.txt 
!define Red-RDIR_bin ${Red-RDIR}\dist
!define Red-RDIR_canvas ${Red-RDIR}\canvas\icons
!define Red-RDIR_widgets ${Red-RDIR}\libraries
!define Red-RDIR_tags ${Red-RDIR}\tagsSystem
!define Red-RDIR_examples ${Red-RDIR}\Examples
!define RDIRECTORY C:\Users\anup\Documents\red\develop\installer\R ;;;; The directory of a blank R so that we don't have to deal with licence terms of R


!define RVER "R-2.9.1"
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
!macro SplitPath PATH
  ; ATTENTION: USE ON YOUR OWN RISK!
  ; Please report bugs here: http://stefan.bertels.org/
  !define Index_SplitPath 'SplitPath_${__LINE__}'
  Push $R0
  StrCpy $R0 "${PATH}" ; $R0 contains PATH
  Push $R1
  Push $R2 ; number of the first "\" of folder part
  Push $R3
  Push $R4
 
  ; check for path type (c:\test or \\server\share\test)
  StrCpy $R2 $R0 2 0
  StrCmp $R2 "\\" 0 ${Index_SplitPath}-nounc
  StrCpy $R2 3
  StrLen $R1 $R0
  StrCpy $R4 -1
${Index_SplitPath}-loop:
  IntOp $R4 $R4 + 1
  IntCmp $R4 $R1 ${Index_SplitPath}-end
  StrCpy $R3 $R0 1 $R4
  StrCmp $R3 "\" 0 ${Index_SplitPath}-loop
  IntCmp $R2 0 ${Index_SplitPath}-split
  IntOp $R2 $R2 - 1
  Goto ${Index_SplitPath}-loop
${Index_SplitPath}-split:
  StrCpy $R1 $R0 "" $R4
  StrCpy $R0 $R0 $R4
  Goto ${Index_SplitPath}-finish
${Index_SplitPath}-end:
  StrCpy $R1 ""
  Goto ${Index_SplitPath}-finish
 
${Index_SplitPath}-nounc:
  StrCpy $R2 $R0 1 1
  StrCmp $R2 ":" 0 ${Index_SplitPath}-fallback
  StrCpy $R1 $R0 "" 2
  StrCpy $R0 $R0 2
  Goto ${Index_SplitPath}-finish
 
${Index_SplitPath}-fallback:
  StrCpy $R1 $R0
  StrCpy $R0 ""
${Index_SplitPath}-finish:
  Pop $R4
  Pop $R3
  Pop $R2
  Exch $R1 ; folder part
  Exch
  Exch $R0 ; drive part
  !undef Index_SplitPath
!macroend

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
    
    SetOutPath $INSTDIR\${RVERSION}\libraries
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_widgets}\*

    SetOutPath $INSTDIR\${RVERSION}\tagsSystem
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_tags}\*

    SetOutPath $INSTDIR\${RVERSION}\Examples
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR_examples}\*

    
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
	
;-------------------------
; Write the registry settings Uninstall
    
    WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${RVERSION}" "DisplayName" "${RVERSION}"
    
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\${RVERSION}" "UninstallString" '"$INSTDIR\${RVERSION}\uninst ${RVERSION}.exe"'

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${RVERSION}\OrangeCanvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$INSTDIR\${RVERSION}\bin\red-RCanvas.exe "%1"';name is appended into the sys.argv variables for opening by Red-R
    
	WriteUninstaller "$INSTDIR\${RVERSION}\uninst ${RVERSION}.exe"

SectionEnd

Section Uninstall
    MessageBox MB_YESNO "Are you sure you want to remove Red-R?" /SD IDYES IDNO end
	
    Delete "$INSTDIR\uninst ${RVERSION}.exe"
    
    RmDir /r /REBOOTOK "$INSTDIR"
	
    RmDir /r /REBOOTOK "$SMPROGRAMS\Red-R\${RVERSION}"
    
    MessageBox MB_YESNO "Would you like to remove your Red-R ${RVERSION} settings?" /SD IDYES IDNO remove_keys
    
        ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
        StrCmp $0 "" 0 +2
          ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
        StrCmp $0 "" +2 0
          RmDir /r /REBOOTOK "$0\red-r\settings"
	
    remove_keys:

    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Red-R\${RVERSION}"
    DeleteRegKey SHELL_CONTEXT "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${RVERSION}"
	
	Delete "$DESKTOP\Red-R Canvas ${RVERSION}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    IfErrors jumpto_iferror jumpto_ifnoerror
    
    jumpto_ifnoerror:
        IfRebootFlag jumpto_IfRebootFlag jumpto_IfNoRebootFlag
        jumpto_IfRebootFlag:
            MessageBox MB_OK "Red-R ${RVERSION} has been successfully removed from your system.$\r$\nYou may need to reboot your machine." /SD IDOK
            Goto end
        jumpto_IfNoRebootFlag:
            MessageBox MB_OK "Red-R ${RVERSION} has been successfully removed from your system." /SD IDOK
            Goto end
        
    jumpto_iferror:
        MessageBox MB_OK "Red-R ${RVERSION} Error!" /SD IDOK

   end:
SectionEnd
