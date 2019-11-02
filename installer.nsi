!include "MUI2.nsh"

!define setup "bubble_sheet_reader_install.exe"
!define srcdir ".\dist\bubble_sheet_reader"
!define company "Ian Sanders"
!define prodname "Bubble Sheet Reader"
!define exec "bubble_sheet_reader\bubble_sheet_reader.exe"

!define icon "assets\icon.ico"

!define regkey "Software\${prodname}"
!define uninstkey "Software\Microsoft\Windows\CurrentVersion\Uninstall\${prodname}"

!define uninstaller "uninstall.exe"

; Settings ---------------------------------------------------------------------

XPStyle off
ShowInstDetails hide
ShowUninstDetails hide

Name "${prodname}"
Caption "${prodname} Installer"

!ifdef icon
  Icon "${srcdir}\${icon}"
  !define MUI_ICON "${srcdir}\${icon}"
!endif

OutFile "${setup}"

SetDateSave on
SetDatablockOptimize on
CRCCheck on
SilentInstall normal

InstallDir "$PROGRAMFILES\${prodname}"
InstallDirRegKey HKLM "${regkey}" ""

; MUI Settings -----------------------------------------------------------------

!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Select a directory to install the program to:"
!define MUI_DIRECTORYPAGE_TEXT_TOP "This will install the ${prodname} utility to your machine.$\r$\n$\r$\nNOTE: If you encounter an 'Error opening file for writing' during installation, abort installation, restart your computer, and try again. If you encounter any futher errors, submit a bug on the project's GitHub page."

!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${regkey}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!define MUI_STARTMENUPAGE_TEXT_CHECKBOX "Don't create start menu folder"

!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "Thank you! ${prodname} installation is complete."
!define MUI_FINISHPAGE_BUTTON "Finish"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${exec}"
!define MUI_FINISHPAGE_RUN_TEXT "Run Bubble Sheet Reader"

; Pages ------------------------------------------------------------------------

Var StartMenuFolder
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

UninstPage uninstConfirm
UninstPage instfiles

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES


AutoCloseWindow false
ShowInstDetails show

Section
  WriteRegStr HKLM "${regkey}" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "${uninstkey}" "DisplayName" "${prodname} (remove only)"
  WriteRegStr HKLM "${uninstkey}" "UninstallString" '"$INSTDIR\${uninstaller}"'

  WriteRegStr HKCR "${prodname}\Shell\open\command\" "" '"$INSTDIR\${exec} "%1"'

  !ifdef icon
    WriteRegStr HKCR "${prodname}\DefaultIcon" "" "$INSTDIR\${icon}"
  !endif

  SetOutPath $INSTDIR

  File /a /r "${srcdir}"

  !ifdef icon
    File /a "${srcdir}\${icon}"
  !endif

  WriteUninstaller "${uninstaller}"
SectionEnd

Section
  SetOutPath $INSTDIR ; for working directory

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    !ifdef icon
      CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${prodname}.lnk" "$INSTDIR\${exec}" "" "$INSTDIR\${icon}"
    !else
      CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${prodname}.lnk" "$INSTDIR\${exec}"
    !endif
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

; Uninstaller ------------------------------------------------------------------
UninstallText "This will uninstall ${prodname}."

!ifdef icon
  UninstallIcon "${srcdir}\${icon}"
!endif

  DeleteRegKey HKLM "${uninstkey}"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

  Delete "$SMPROGRAMS\$StartMenuFolder\*.*"
  Delete "$SMPROGRAMS\$StartMenuFolder"

  !ifdef licensefile
    Delete "$INSTDIR\${licensefile}"
  !endif

  !ifdef notefile
    Delete "$INSTDIR\${notefile}"
  !endif

  !ifdef icon
    Delete "$INSTDIR\${icon}"
  !endif

  Delete "$INSTDIR"

  !ifdef unfiles
    !include "${unfiles}"
  !endif

  DeleteRegKey HKLM "${regkey}"
SectionEnd