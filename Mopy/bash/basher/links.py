# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2014 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================

"""Links initialization functions. Each panel's UIlIst has main and items Links
attributes which are populated here. Therefore the order of menu items is
also defined in these functions."""

import os
import win32gui
from . import InstallersPanel, InstallersList, INIList, ModList, SaveList, \
    BSAList, ScreensList, MessageList, MasterList, bEnableWizard,  PeopleList,\
    BashStatusBar, Tab_Link
from .constants import PNG, BMP, TIF, ICO, JPEG
from .. import balt, bosh, bush
from ..cint import CBash
from ..balt import Image, MenuLink, SeparatorLink
from ..bolt import deprint, GPath
# modules below define the __all__ directive
from .app_buttons import *
from .mods_links import *
from .files_links import *
from .installers_links import *
from .installer_links import *
from .saves_links import *
from .settings_links import *
from .misc_links import *
from .ini_links import *
from .mod_links import *

#------------------------------------------------------------------------------
def initAppLinks(appDir):
    #-- Other tools
    links = {}
    try:
        import win32com.client
        sh = win32com.client.Dispatch('WScript.Shell')
        shCreateShortCut = sh.CreateShortCut
        appDirJoin = appDir.join
        for file_ in appDir.list():
            file_ = appDirJoin(file_)
            if file_.isfile() and file_.cext == u'.lnk':
                fileS = file_.s
                shortcut = shCreateShortCut(fileS)
                description = shortcut.Description
                if not description:
                    description = u' '.join((_(u'Launch'), file_.sbody))
                links[fileS] = (shortcut.TargetPath, shortcut.WorkingDirectory,
                                shortcut.Arguments, shortcut.IconLocation,
                                description)
        return links
    except:
        deprint(_(u"Error initializing links:"),traceback=True)

def InitStatusBar():
    """Initialize status bar links."""
    dirImages = bosh.dirs['images']
    def imageList(template):
        return [Image(dirImages.join(template % x)) for x in (16,24,32)]
    #--Bash Status/LinkBar
    BashStatusBar.obseButton = obseButton = Obse_Button(uid=u'OBSE')
    BashStatusBar.buttons.append(obseButton)
    BashStatusBar.laaButton = laaButton = LAA_Button(uid=u'LAA')
    BashStatusBar.buttons.append(laaButton)
    BashStatusBar.buttons.append(AutoQuit_Button(uid=u'AutoQuit'))
    BashStatusBar.buttons.append( # Game
        Game_Button(
            bosh.dirs['app'].join(bush.game.exe),
            imageList(u'%s%%s.png' % bush.game.fsName.lower()),
            u' '.join((_(u"Launch"),bush.game.displayName)),
            u' '.join((_(u"Launch"),bush.game.displayName,u'%(version)s')),
            u'',
            uid=u'Oblivion'))
    BashStatusBar.buttons.append( #TESCS/CreationKit
        TESCS_Button(
            bosh.dirs['app'].join(bush.game.cs.exe),
            imageList(bush.game.cs.imageName),
            u' '.join((_(u"Launch"),bush.game.cs.shortName)),
            u' '.join((_(u"Launch"),bush.game.cs.shortName,u'%(version)s')),
            bush.game.cs.seArgs,
            uid=u'TESCS'))
    BashStatusBar.buttons.append( #OBMM
        App_Button(
            bosh.dirs['app'].join(u'OblivionModManager.exe'),
            imageList(u'obmm%s.png'),
            _(u"Launch OBMM"),
            uid=u'OBMM'))
    from .constants import toolbar_buttons, app_buttons
    for tb in toolbar_buttons:
        BashStatusBar.buttons.append(Tooldir_Button(*tb))
    for ab in app_buttons:
        BashStatusBar.buttons.append(App_Button(*ab[:-1], **ab[-1]))
    BashStatusBar.buttons.append( #Tes4View
        App_Tes4View(
            (bosh.tooldirs['Tes4ViewPath'],u'-TES4'), #no cmd argument to force view mode
            imageList(u'tools/tes4view%s.png'),
            _(u"Launch TES4View"),
            uid=u'TES4View'))
    BashStatusBar.buttons.append( #Tes4Edit
        App_Tes4View(
            (bosh.tooldirs['Tes4EditPath'],u'-TES4 -edit'),
            imageList(u'tools/tes4edit%s.png'),
            _(u"Launch TES4Edit"),
            uid=u'TES4Edit'))
    BashStatusBar.buttons.append( #Tes5Edit
        App_Tes4View(
            (bosh.tooldirs['Tes5EditPath'],u'-TES5 -edit'),
            imageList(u'tools/tes4edit%s.png'),
            _(u"Launch TES5Edit"),
            uid=u'TES5Edit'))
    BashStatusBar.buttons.append( #TesVGecko
        App_Button( (bosh.tooldirs['Tes5GeckoPath']),
            imageList(u'tools/tesvgecko%s.png'),
            _(u"Launch TesVGecko"),
            uid=u'TesVGecko'))
    BashStatusBar.buttons.append( #Tes4Trans
        App_Tes4View(
            (bosh.tooldirs['Tes4TransPath'],u'-TES4 -translate'),
            imageList(u'tools/tes4trans%s.png'),
            _(u"Launch TES4Trans"),
            uid=u'TES4Trans'))
    BashStatusBar.buttons.append( #Tes4LODGen
        App_Tes4View(
            (bosh.tooldirs['Tes4LodGenPath'],u'-TES4 -lodgen'),
            imageList(u'tools/tes4lodgen%s.png'),
            _(u"Launch Tes4LODGen"),
            uid=u'TES4LODGen'))
    BashStatusBar.buttons.append( #BOSS
        App_BOSS(
            (bosh.tooldirs['boss']),
            imageList(u'boss%s.png'),
            _(u"Launch BOSS"),
            uid=u'BOSS'))
    if bosh.inisettings['ShowModelingToolLaunchers']:
        from .constants import modeling_tools_buttons
        for mb in modeling_tools_buttons:
            BashStatusBar.buttons.append(Tooldir_Button(*mb))
        BashStatusBar.buttons.append( #Softimage Mod Tool
            App_Button(
                (bosh.tooldirs['SoftimageModTool'],u'-mod'),
                imageList(u'tools/softimagemodtool%s.png'),
                _(u"Launch Softimage Mod Tool"),
                uid=u'SoftimageModTool'))
    if bosh.inisettings['ShowModelingToolLaunchers'] \
            or bosh.inisettings['ShowTextureToolLaunchers']:
        BashStatusBar.buttons.append( #Nifskope
            Tooldir_Button('NifskopePath', imageList(u'tools/nifskope%s.png'),
                _(u"Launch Nifskope")))
    if bosh.inisettings['ShowTextureToolLaunchers']:
        from .constants import texture_tool_buttons
        for tt in texture_tool_buttons:
            BashStatusBar.buttons.append(Tooldir_Button(*tt))
    if bosh.inisettings['ShowAudioToolLaunchers']:
        from .constants import audio_tools
        for at in audio_tools:
            BashStatusBar.buttons.append(Tooldir_Button(*at))
    from .constants import misc_tools
    for mt in misc_tools: BashStatusBar.buttons.append(Tooldir_Button(*mt))
    #--Custom Apps
    dirApps = bosh.dirs['mopy'].join(u'Apps')
    appLinks = initAppLinks(dirApps)
    folderIcon = None
    badIcons = [Image(bosh.dirs['images'].join(u'x.png'))] * 3
    for link in appLinks:
        (target,workingdir,args,icon,description) = appLinks[link]
        path = dirApps.join(link)
        if target.lower().find(ur'installer\{') != -1:
            target = path
        else:
            target = GPath(target)
        if target.exists():
            icon,idex = icon.split(u',')
            if icon == u'':
                if target.cext == u'.exe':
                    # Use the icon embedded in the exe
                    try:
                        win32gui.ExtractIcon(0, target.s, 0)
                        icon = target
                    except:
                        icon = u'' # Icon will be set to a red x further down.
                else:
                    # Use the default icon for that file type
                    try:
                        import _winreg
                        if target.isdir():
                            if folderIcon is None:
                                # Special handling of the Folder icon
                                folderkey = _winreg.OpenKey(
                                    _winreg.HKEY_CLASSES_ROOT,
                                    u'Folder')
                                iconkey = _winreg.OpenKey(
                                    folderkey,
                                    u'DefaultIcon')
                                filedata = _winreg.EnumValue(
                                    iconkey,0)
                                filedata = filedata[1]
                                folderIcon = filedata
                            else:
                                filedata = folderIcon
                        else:
                            icon_path = _winreg.QueryValue(
                                _winreg.HKEY_CLASSES_ROOT,
                                target.cext)
                            pathKey = _winreg.OpenKey(
                                _winreg.HKEY_CLASSES_ROOT,
                                u'%s\\DefaultIcon' % icon_path)
                            filedata = _winreg.EnumValue(pathKey, 0)[1]
                            _winreg.CloseKey(pathKey)
                        icon,idex = filedata.split(u',')
                        icon = os.path.expandvars(icon)
                        if not os.path.isabs(icon):
                            # Get the correct path to the dll
                            for dir in os.environ['PATH'].split(u';'):
                                test = GPath(dir).join(icon)
                                if test.exists():
                                    icon = test
                                    break
                    except:
                        deprint(_(u'Error finding icon for %s:') % target.s,traceback=True)
                        icon = u'not\\a\\path'
            icon = GPath(icon)
            # First try a custom icon
            fileName = u'%s%%i.png' % path.sbody
            customIcons = [dirApps.join(fileName % x) for x in (16,24,32)]
            if customIcons[0].exists():
                icon = customIcons
            # Next try the shortcut specified icon
            else:
                if icon.exists():
                    fileName = u';'.join((icon.s,idex))
                    icon = [Image(fileName,ICO,x) for x in (16,24,32)]
            # Last, use the 'x' icon
                else:
                    icon = badIcons
            BashStatusBar.buttons.append(
                App_Button(
                    (path,()),
                    icon, description,
                    canHide=False
                    ))
    #--Final couple
    BashStatusBar.buttons.append(
        App_Button(
            (bosh.dirs['mopy'].join(u'Wrye Bash Launcher.pyw'), u'-d', u'--bashmon'),
            imageList(u'bashmon%s.png'),
            _(u"Launch BashMon"),
            uid=u'Bashmon'))
    BashStatusBar.buttons.append(App_DocBrowser(uid=u'DocBrowser'))
    BashStatusBar.buttons.append(App_ModChecker(uid=u'ModChecker'))
    BashStatusBar.buttons.append(App_Settings(uid=u'Settings',canHide=False))
    BashStatusBar.buttons.append(App_Help(uid=u'Help',canHide=False))
    if bosh.inisettings['ShowDevTools']:
        BashStatusBar.buttons.append(App_Restart(uid=u'Restart'))
        BashStatusBar.buttons.append(App_GenPickle(uid=u'Generate PKL File'))

#------------------------------------------------------------------------------
def InitMasterLinks():
    """Initialize master list menus."""
    #--MasterList: Column Links
    if True: #--Sort by
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(Mods_EsmsFirst())
        sortMenu.links.append(SeparatorLink())
        sortMenu.links.append(Files_SortBy('File'))
        sortMenu.links.append(Files_SortBy('Author'))
        sortMenu.links.append(Files_SortBy('Group'))
        sortMenu.links.append(Files_SortBy('Installer'))
        sortMenu.links.append(Files_SortBy('Load Order'))
        sortMenu.links.append(Files_SortBy('Modified'))
        sortMenu.links.append(Files_SortBy('Save Order'))
        sortMenu.links.append(Files_SortBy('Status'))
        MasterList.mainMenu.append(sortMenu)

    #--MasterList: Item Links
    MasterList.itemMenu.append(Master_ChangeTo())
    MasterList.itemMenu.append(Master_Disable())

#------------------------------------------------------------------------------
def InitInstallerLinks():
    """Initialize Installers tab menus."""
    #--Column links
    #--Sorting
    if True:
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(Installers_SortActive())
        sortMenu.links.append(Installers_SortProjects())
        #InstallersList.mainMenu.append(Installers_SortStructure())
        sortMenu.links.append(SeparatorLink())
        sortMenu.links.append(Files_SortBy('Package'))
        sortMenu.links.append(Files_SortBy('Order'))
        sortMenu.links.append(Files_SortBy('Modified'))
        sortMenu.links.append(Files_SortBy('Size'))
        sortMenu.links.append(Files_SortBy('Files'))
        InstallersList.mainMenu.append(sortMenu)
    #--Columns
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(List_Columns('bash.installers.cols','bash.installers.allCols',['Package']))
    #--Actions
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(balt.Tanks_Open())
    InstallersList.mainMenu.append(Installers_Refresh(fullRefresh=False))
    InstallersList.mainMenu.append(Installers_Refresh(fullRefresh=True))
    InstallersList.mainMenu.append(Installers_AddMarker())
    InstallersList.mainMenu.append(Installers_CreateNewProject())
    InstallersList.mainMenu.append(Installers_MonitorInstall())
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_ListPackages())
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_AnnealAll())
    InstallersList.mainMenu.append(Files_Unhide('installer'))
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_UninstallAllPackages())
    InstallersList.mainMenu.append(Installers_UninstallAllUnknownFiles())
    #--Behavior
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_AvoidOnStart())
    InstallersList.mainMenu.append(Installers_Enabled())
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_AutoAnneal())
    if bEnableWizard:
        InstallersList.mainMenu.append(Installers_AutoWizard())
    InstallersList.mainMenu.append(Installers_AutoRefreshProjects())
    InstallersList.mainMenu.append(Installers_AutoRefreshBethsoft())
    InstallersList.mainMenu.append(Installers_AutoApplyEmbeddedBCFs())
    InstallersList.mainMenu.append(Installers_BsaRedirection())
    InstallersList.mainMenu.append(Installers_RemoveEmptyDirs())
    InstallersList.mainMenu.append(Installers_ConflictsReportShowsInactive())
    InstallersList.mainMenu.append(Installers_ConflictsReportShowsLower())
    InstallersList.mainMenu.append(Installers_ConflictsReportShowBSAConflicts())
    InstallersList.mainMenu.append(Installers_WizardOverlay())
    InstallersList.mainMenu.append(SeparatorLink())
    InstallersList.mainMenu.append(Installers_SkipOBSEPlugins())
    InstallersList.mainMenu.append(Installers_SkipScreenshots())
    InstallersList.mainMenu.append(Installers_SkipImages())
    InstallersList.mainMenu.append(Installers_SkipDocs())
    InstallersList.mainMenu.append(Installers_SkipDistantLOD())
    InstallersList.mainMenu.append(Installers_SkipLandscapeLODMeshes())
    InstallersList.mainMenu.append(Installers_SkipLandscapeLODTextures())
    InstallersList.mainMenu.append(Installers_SkipLandscapeLODNormals())
    InstallersList.mainMenu.append(Installers_RenameStrings())

    #--Item links
    #--File
    InstallersList.itemMenu.append(Installer_Open())
    InstallersList.itemMenu.append(Installer_Duplicate())
    InstallersList.itemMenu.append(Installer_Delete())
    if True: #--Open At...
        openAtMenu = InstallerOpenAt_MainMenu(_(u"Open at"), oneDatumOnly=True)
        openAtMenu.links.append(Installer_OpenSearch())
        openAtMenu.links.append(Installer_OpenNexus())
        openAtMenu.links.append(Installer_OpenTESA())
        openAtMenu.links.append(Installer_OpenPES())
        InstallersList.itemMenu.append(openAtMenu)
    InstallersList.itemMenu.append(Installer_Hide())
    InstallersList.itemMenu.append(Installer_Rename())
    #--Install, uninstall, etc.
    InstallersList.itemMenu.append(SeparatorLink())
    InstallersList.itemMenu.append(Installer_Refresh())
    InstallersList.itemMenu.append(Installer_Move())
    InstallersList.itemMenu.append(SeparatorLink())
    InstallersList.itemMenu.append(Installer_HasExtraData())
    InstallersList.itemMenu.append(Installer_OverrideSkips())
    InstallersList.itemMenu.append(Installer_SkipVoices())
    InstallersList.itemMenu.append(Installer_SkipRefresh())
    InstallersList.itemMenu.append(SeparatorLink())
    if bEnableWizard:
        InstallersList.itemMenu.append(Installer_Wizard(False))
        InstallersList.itemMenu.append(Installer_Wizard(True))
        InstallersList.itemMenu.append(Installer_EditWizard())
        InstallersList.itemMenu.append(SeparatorLink())
    InstallersList.itemMenu.append(Installer_OpenReadme())
    InstallersList.itemMenu.append(Installer_Anneal())
    InstallersList.itemMenu.append(Installer_Install())
    InstallersList.itemMenu.append(Installer_Install('LAST'))
    InstallersList.itemMenu.append(Installer_Install('MISSING'))
    InstallersList.itemMenu.append(Installer_Uninstall())
    InstallersList.itemMenu.append(SeparatorLink())
    #--Build
    if True: #--BAIN Conversion
        conversionsMenu = InstallerConverter_MainMenu(_(u"Conversions"))
        conversionsMenu.links.append(InstallerConverter_Create())
        conversionsMenu.links.append(InstallerConverter_ConvertMenu(_(u"Apply")))
        InstallersList.itemMenu.append(conversionsMenu)
    InstallersList.itemMenu.append(InstallerProject_Pack())
    InstallersList.itemMenu.append(InstallerArchive_Unpack())
    InstallersList.itemMenu.append(InstallerProject_ReleasePack())
    InstallersList.itemMenu.append(InstallerProject_Sync())
    InstallersList.itemMenu.append(Installer_CopyConflicts())
    InstallersList.itemMenu.append(InstallerProject_OmodConfig())
    InstallersList.itemMenu.append(Installer_ListStructure())

    #--espms Main Menu
    InstallersPanel.espmMenu.append(Installer_Espm_SelectAll())
    InstallersPanel.espmMenu.append(Installer_Espm_DeselectAll())
    InstallersPanel.espmMenu.append(Installer_Espm_List())
    InstallersPanel.espmMenu.append(SeparatorLink())
    #--espms Item Menu
    InstallersPanel.espmMenu.append(Installer_Espm_Rename())
    InstallersPanel.espmMenu.append(Installer_Espm_Reset())
    InstallersPanel.espmMenu.append(SeparatorLink())
    InstallersPanel.espmMenu.append(Installer_Espm_ResetAll())

    #--Sub-Package Main Menu
    InstallersPanel.subsMenu.append(Installer_Subs_SelectAll())
    InstallersPanel.subsMenu.append(Installer_Subs_DeselectAll())
    InstallersPanel.subsMenu.append(Installer_Subs_ToggleSelection())
    InstallersPanel.subsMenu.append(SeparatorLink())
    InstallersPanel.subsMenu.append(Installer_Subs_ListSubPackages())

#------------------------------------------------------------------------------
def InitINILinks():
    """Initialize INI Edits tab menus."""
    #--Column Links
    if True: #--Sort by
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(INI_SortValid())
        sortMenu.links.append(SeparatorLink())
        sortMenu.links.append(Files_SortBy('File'))
        sortMenu.links.append(Files_SortBy('Installer'))
        INIList.mainMenu.append(sortMenu)
    INIList.mainMenu.append(SeparatorLink())
    INIList.mainMenu.append(List_Columns('bash.ini.cols','bash.ini.allCols',['File']))
    INIList.mainMenu.append(SeparatorLink())
    INIList.mainMenu.append(INI_AllowNewLines())
    INIList.mainMenu.append(Files_Open())
    INIList.mainMenu.append(INI_ListINIs())

    #--Item menu
    INIList.itemMenu.append(INI_Apply())
    INIList.itemMenu.append(INI_CreateNew())
    INIList.itemMenu.append(INI_ListErrors())
    INIList.itemMenu.append(SeparatorLink())
    INIList.itemMenu.append(INI_FileOpenOrCopy())
    INIList.itemMenu.append(INI_Delete())

#------------------------------------------------------------------------------
def InitModLinks():
    """Initialize Mods tab menus."""
    #--ModList: Column Links
    if True: #--Load
        loadMenu = MenuLink(_(u"Load"))
        loadMenu.links.append(Mods_LoadList())
        ModList.mainMenu.append(loadMenu)
    if True: #--Sort by
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(Mods_EsmsFirst())
        sortMenu.links.append(Mods_SelectedFirst())
        sortMenu.links.append(SeparatorLink())
        sortMenu.links.append(Files_SortBy('File'))
        sortMenu.links.append(Files_SortBy('Author'))
        sortMenu.links.append(Files_SortBy('Group'))
        sortMenu.links.append(Files_SortBy('Installer'))
        sortMenu.links.append(Files_SortBy('Load Order'))
        sortMenu.links.append(Files_SortBy('Modified'))
        sortMenu.links.append(Files_SortBy('Rating'))
        sortMenu.links.append(Files_SortBy('Size'))
        sortMenu.links.append(Files_SortBy('Status'))
        sortMenu.links.append(Files_SortBy('CRC'))
        sortMenu.links.append(Files_SortBy('Mod Status'))
        ModList.mainMenu.append(sortMenu)
    if bush.game.fsName == u'Oblivion': #--Versions
        versionsMenu = MenuLink(u"Oblivion.esm")
        versionsMenu.links.append(Mods_OblivionVersion(u'1.1'))
        versionsMenu.links.append(Mods_OblivionVersion(u'1.1b'))
        versionsMenu.links.append(Mods_OblivionVersion(u'GOTY non-SI'))
        versionsMenu.links.append(Mods_OblivionVersion(u'SI'))
        ModList.mainMenu.append(versionsMenu)
    #--Columns ----------------------------------
    ModList.mainMenu.append(SeparatorLink())
    ModList.mainMenu.append(List_Columns('bash.mods.cols','bash.mods.allCols',['File']))
    #--------------------------------------------
    ModList.mainMenu.append(SeparatorLink())
    #--File Menu---------------------------------
    if True:
        fileMenu = MenuLink(_(u'File'))
        if bush.game.esp.canBash:
            fileMenu.links.append(Mods_CreateBlankBashedPatch())
            fileMenu.links.append(Mods_CreateBlank())
            fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(Files_Open())
        fileMenu.links.append(Files_Unhide('mod'))
        ModList.mainMenu.append(fileMenu)
    ModList.mainMenu.append(SeparatorLink())
    ModList.mainMenu.append(Mods_ListMods())
    ModList.mainMenu.append(Mods_ListBashTags())
    ModList.mainMenu.append(Mods_CleanDummyMasters())
    ModList.mainMenu.append(SeparatorLink())
    ModList.mainMenu.append(Mods_AutoGhost())
    if bush.game.fsName != u'Skyrim':
        ModList.mainMenu.append(Mods_LockTimes())
    ModList.mainMenu.append(Mods_ScanDirty())

    #--ModList: Item Links
    if bosh.inisettings['ShowDevTools']:
        ModList.itemMenu.append(Mod_FullLoad())
    if True: #--File
        fileMenu = MenuLink(_(u"File"))
        if bush.game.esp.canBash:
            fileMenu.links.append(Mod_CreateDummyMasters())
            fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_Backup())
        fileMenu.links.append(File_Duplicate())
        fileMenu.links.append(File_Snapshot())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_Delete())
        fileMenu.links.append(File_Hide())
        fileMenu.links.append(File_Redate())
        fileMenu.links.append(File_Sort())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_RevertToBackup())
        fileMenu.links.append(File_RevertToSnapshot())
        ModList.itemMenu.append(fileMenu)
    if True: #--Groups
        groupMenu = MenuLink(_(u"Groups"))
        groupMenu.links.append(Mod_Groups())
        ModList.itemMenu.append(groupMenu)
    if True: #--Ratings
        ratingMenu = MenuLink(_(u"Rating"))
        ratingMenu.links.append(Mod_Ratings())
        ModList.itemMenu.append(ratingMenu)
    #--------------------------------------------
    ModList.itemMenu.append(SeparatorLink())
    if bush.game.esp.canBash:
        ModList.itemMenu.append(Mod_Details())
    ModList.itemMenu.append(File_ListMasters())
    ModList.itemMenu.append(Mod_ShowReadme())
    ModList.itemMenu.append(Mod_ListBashTags())
    ModList.itemMenu.append(Mod_CreateBOSSReport())
    ModList.itemMenu.append(Mod_CopyModInfo())
    #--------------------------------------------
    ModList.itemMenu.append(SeparatorLink())
    ModList.itemMenu.append(Mod_AllowGhosting())
    ModList.itemMenu.append(Mod_Ghost())
    if bush.game.esp.canBash:
        ModList.itemMenu.append(SeparatorLink())
        ModList.itemMenu.append(Mod_MarkMergeable(False))
        if CBash:
            ModList.itemMenu.append(Mod_MarkMergeable(True))
        ModList.itemMenu.append(Mod_Patch_Update(False))
        if CBash:
            ModList.itemMenu.append(Mod_Patch_Update(True))
        ModList.itemMenu.append(Mod_ListPatchConfig())
        ModList.itemMenu.append(Mod_ExportPatchConfig())
        #--Advanced
        ModList.itemMenu.append(SeparatorLink())
        if True: #--Export
            exportMenu = MenuLink(_(u"Export"))
            exportMenu.links.append(CBash_Mod_CellBlockInfo_Export())
            exportMenu.links.append(Mod_EditorIds_Export())
    ##        exportMenu.links.append(Mod_ItemData_Export())
            if bush.game.fsName == u'Skyrim':
                exportMenu.links.append(Mod_FullNames_Export())
                exportMenu.links.append(Mod_Prices_Export())
                exportMenu.links.append(Mod_Stats_Export())
            elif bush.game.fsName == u'Oblivion':
                exportMenu.links.append(Mod_Factions_Export())
                exportMenu.links.append(Mod_FullNames_Export())
                exportMenu.links.append(Mod_ActorLevels_Export())
                exportMenu.links.append(CBash_Mod_MapMarkers_Export())
                exportMenu.links.append(Mod_Prices_Export())
                exportMenu.links.append(Mod_FactionRelations_Export())
                exportMenu.links.append(Mod_IngredientDetails_Export())
                exportMenu.links.append(Mod_Scripts_Export())
                exportMenu.links.append(Mod_SigilStoneDetails_Export())
                exportMenu.links.append(Mod_SpellRecords_Export())
                exportMenu.links.append(Mod_Stats_Export())
            ModList.itemMenu.append(exportMenu)
        if True: #--Import
            importMenu = MenuLink(_(u"Import"))
            importMenu.links.append(Mod_EditorIds_Import())
    ##        importMenu.links.append(Mod_ItemData_Import())
            if bush.game.fsName == u'Skyrim':
                importMenu.links.append(Mod_FullNames_Import())
                importMenu.links.append(Mod_Prices_Import())
                importMenu.links.append(Mod_Stats_Import())
            elif bush.game.fsName == u'Oblivion':
                importMenu.links.append(Mod_Factions_Import())
                importMenu.links.append(Mod_FullNames_Import())
                importMenu.links.append(Mod_ActorLevels_Import())
                importMenu.links.append(CBash_Mod_MapMarkers_Import())
                importMenu.links.append(Mod_Prices_Import())
                importMenu.links.append(Mod_FactionRelations_Import())
                importMenu.links.append(Mod_IngredientDetails_Import())
                importMenu.links.append(Mod_Scripts_Import())
                importMenu.links.append(Mod_SigilStoneDetails_Import())
                importMenu.links.append(Mod_SpellRecords_Import())
                importMenu.links.append(Mod_Stats_Import())
                importMenu.links.append(SeparatorLink())
                importMenu.links.append(Mod_Face_Import())
                importMenu.links.append(Mod_Fids_Replace())
            ModList.itemMenu.append(importMenu)
        if True: #--Cleaning
            cleanMenu = MenuLink(_(u"Mod Cleaning"))
            cleanMenu.links.append(Mod_SkipDirtyCheck())
            cleanMenu.links.append(SeparatorLink())
            cleanMenu.links.append(Mod_ScanDirty())
            cleanMenu.links.append(Mod_RemoveWorldOrphans())
            cleanMenu.links.append(Mod_CleanMod())
            cleanMenu.links.append(Mod_UndeleteRefs())
            ModList.itemMenu.append(cleanMenu)
        ModList.itemMenu.append(Mod_AddMaster())
        ModList.itemMenu.append(Mod_CopyToEsmp())
        if bush.game.fsName != u'Skyrim':
            ModList.itemMenu.append(Mod_DecompileAll())
        ModList.itemMenu.append(Mod_FlipSelf())
        ModList.itemMenu.append(Mod_FlipMasters())
        if bush.game.fsName == u'Oblivion':
            ModList.itemMenu.append(Mod_SetVersion())
#    if bosh.inisettings['showadvanced'] == 1:
#        advmenu = MenuLink(_(u"Advanced Scripts"))
#        advmenu.links.append(Mod_DiffScripts())
        #advmenu.links.append(())

#------------------------------------------------------------------------------
def InitSaveLinks():
    """Initialize save tab menus."""
    #--SaveList: Column Links
    if True: #--Sort
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(Files_SortBy('File'))
        sortMenu.links.append(Files_SortBy('Cell'))
        sortMenu.links.append(Files_SortBy('PlayTime'))
        sortMenu.links.append(Files_SortBy('Modified'))
        sortMenu.links.append(Files_SortBy('Player'))
        sortMenu.links.append(Files_SortBy('Status'))
        SaveList.mainMenu.append(sortMenu)
    if bush.game.fsName == u'Oblivion': #--Versions
        versionsMenu = MenuLink(u"Oblivion.esm")
        versionsMenu.links.append(Mods_OblivionVersion(u'1.1',True))
        versionsMenu.links.append(Mods_OblivionVersion(u'1.1b',True))
        versionsMenu.links.append(Mods_OblivionVersion(u'GOTY non-SI',True))
        versionsMenu.links.append(Mods_OblivionVersion(u'SI',True))
        SaveList.mainMenu.append(versionsMenu)
    if True: #--Save Profiles
        subDirMenu = MenuLink(_(u"Profile"))
        subDirMenu.links.append(Saves_Profiles())
        SaveList.mainMenu.append(subDirMenu)
    #--Columns --------------------------------
    SaveList.mainMenu.append(SeparatorLink())
    SaveList.mainMenu.append(List_Columns('bash.saves.cols','bash.saves.allCols',['File']))
    #------------------------------------------
    SaveList.mainMenu.append(SeparatorLink())
    SaveList.mainMenu.append(Files_Open())
    SaveList.mainMenu.append(Files_Unhide('save'))

    #--SaveList: Item Links
    if True: #--File
        fileMenu = MenuLink(_(u"File")) #>>
        fileMenu.links.append(File_Backup())
        fileMenu.links.append(File_Duplicate())
        #fileMenu.links.append(File_Snapshot())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_Delete())
        fileMenu.links.append(File_Hide())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_RevertToBackup())
        fileMenu.links.append(Save_Rename())
        fileMenu.links.append(Save_Renumber())
        #fileMenu.links.append(File_RevertToSnapshot())
        SaveList.itemMenu.append(fileMenu)
    if True: #--Move to Profile
        moveMenu = MenuLink(_(u"Move To"))
        moveMenu.links.append(Save_Move())
        SaveList.itemMenu.append(moveMenu)
    if True: #--Copy to Profile
        copyMenu = MenuLink(_(u"Copy To"))
        copyMenu.links.append(Save_Move(True))
        SaveList.itemMenu.append(copyMenu)
    #--------------------------------------------
    SaveList.itemMenu.append(SeparatorLink())
    SaveList.itemMenu.append(Save_LoadMasters())
    SaveList.itemMenu.append(File_ListMasters())
    SaveList.itemMenu.append(Save_DiffMasters())
    if bush.game.ess.canEditMore:
        SaveList.itemMenu.append(Save_Stats())
        SaveList.itemMenu.append(Save_StatObse())
        #--------------------------------------------
        SaveList.itemMenu.append(SeparatorLink())
        SaveList.itemMenu.append(Save_EditPCSpells())
        SaveList.itemMenu.append(Save_RenamePlayer())
        SaveList.itemMenu.append(Save_EditCreatedEnchantmentCosts())
        SaveList.itemMenu.append(Save_ImportFace())
        SaveList.itemMenu.append(Save_EditCreated('ENCH'))
        SaveList.itemMenu.append(Save_EditCreated('ALCH'))
        SaveList.itemMenu.append(Save_EditCreated('SPEL'))
        SaveList.itemMenu.append(Save_ReweighPotions())
        SaveList.itemMenu.append(Save_UpdateNPCLevels())
    #--------------------------------------------
    SaveList.itemMenu.append(SeparatorLink())
    SaveList.itemMenu.append(Save_ExportScreenshot())
    #--------------------------------------------
    if bush.game.ess.canEditMore:
        SaveList.itemMenu.append(SeparatorLink())
        SaveList.itemMenu.append(Save_Unbloat())
        SaveList.itemMenu.append(Save_RepairAbomb())
        SaveList.itemMenu.append(Save_RepairFactions())
        SaveList.itemMenu.append(Save_RepairHair())

#------------------------------------------------------------------------------
def InitBSALinks():
    """Initialize save tab menus."""
    #--BSAList: Column Links
    if True: #--Sort
        sortMenu = MenuLink(_(u"Sort by"))
        sortMenu.links.append(Files_SortBy('File'))
        sortMenu.links.append(Files_SortBy('Modified'))
        sortMenu.links.append(Files_SortBy('Size'))
        BSAList.mainMenu.append(sortMenu)
    BSAList.mainMenu.append(SeparatorLink())
    BSAList.mainMenu.append(Files_Open())
    BSAList.mainMenu.append(Files_Unhide('save'))

    #--BSAList: Item Links
    if True: #--File
        fileMenu = MenuLink(_(u"File")) #>>
        fileMenu.links.append(File_Backup())
        fileMenu.links.append(File_Duplicate())
        #fileMenu.links.append(File_Snapshot())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_Delete())
        fileMenu.links.append(File_Hide())
        fileMenu.links.append(SeparatorLink())
        fileMenu.links.append(File_RevertToBackup())
        #fileMenu.links.append(File_RevertToSnapshot())
        BSAList.itemMenu.append(fileMenu)
    #--------------------------------------------
    BSAList.itemMenu.append(SeparatorLink())
    BSAList.itemMenu.append(Save_LoadMasters())
    BSAList.itemMenu.append(File_ListMasters())
    BSAList.itemMenu.append(Save_DiffMasters())
    BSAList.itemMenu.append(Save_Stats())
    #--------------------------------------------
    BSAList.itemMenu.append(SeparatorLink())
    BSAList.itemMenu.append(Save_EditPCSpells())
    BSAList.itemMenu.append(Save_ImportFace())
    BSAList.itemMenu.append(Save_EditCreated('ENCH'))
    BSAList.itemMenu.append(Save_EditCreated('ALCH'))
    BSAList.itemMenu.append(Save_EditCreated('SPEL'))
    BSAList.itemMenu.append(Save_ReweighPotions())
    BSAList.itemMenu.append(Save_UpdateNPCLevels())
    #--------------------------------------------
    BSAList.itemMenu.append(SeparatorLink())
    BSAList.itemMenu.append(Save_Unbloat())
    BSAList.itemMenu.append(Save_RepairAbomb())
    BSAList.itemMenu.append(Save_RepairFactions())
    BSAList.itemMenu.append(Save_RepairHair())

#------------------------------------------------------------------------------
def InitScreenLinks():
    """Initialize screens tab menus."""
    #--SaveList: Column Links
    ScreensList.mainMenu.append(Files_Open())
    ScreensList.mainMenu.append(SeparatorLink())
    ScreensList.mainMenu.append(List_Columns('bash.screens.cols','bash.screens.allCols',['File']))
    ScreensList.mainMenu.append(SeparatorLink())
    ScreensList.mainMenu.append(Screens_NextScreenShot())
    #--JPEG Quality
    if True:
        qualityMenu = MenuLink(_(u'JPEG Quality'))
        for i in range(100,80,-5):
            qualityMenu.links.append(Screen_JpgQuality(i))
        qualityMenu.links.append(Screen_JpgQualityCustom())
        ScreensList.mainMenu.append(SeparatorLink())
        ScreensList.mainMenu.append(qualityMenu)

    #--ScreensList: Item Links
    ScreensList.itemMenu.append(File_Open())
    ScreensList.itemMenu.append(Screen_Rename())
    ScreensList.itemMenu.append(File_Delete())
    ScreensList.itemMenu.append(SeparatorLink())
    if True: #--Convert
        convertMenu = MenuLink(_(u'Convert'))
        convertMenu.links.append(Screen_ConvertTo(u'jpg',JPEG))
        convertMenu.links.append(Screen_ConvertTo(u'png',PNG))
        convertMenu.links.append(Screen_ConvertTo(u'bmp',BMP))
        convertMenu.links.append(Screen_ConvertTo(u'tif',TIF))
        ScreensList.itemMenu.append(convertMenu)

#------------------------------------------------------------------------------
def InitMessageLinks():
    """Initialize messages tab menus."""
    #--SaveList: Column Links
    MessageList.mainMenu.append(Messages_Archive_Import())
    MessageList.mainMenu.append(SeparatorLink())
    MessageList.mainMenu.append(List_Columns('bash.messages.cols','bash.messages.allCols',['Subject']))

    #--ScreensList: Item Links
    MessageList.itemMenu.append(Message_Delete())

#------------------------------------------------------------------------------
def InitPeopleLinks():
    """Initialize people tab menus."""
    #--Header links
    PeopleList.mainMenu.append(People_AddNew())
    PeopleList.mainMenu.append(People_Import())
    PeopleList.mainMenu.append(SeparatorLink())
    PeopleList.mainMenu.append(List_Columns('bash.people.cols','bash.people.allCols',['Name']))
    #--Item links
    PeopleList.itemMenu.append(People_Karma())
    PeopleList.itemMenu.append(SeparatorLink())
    PeopleList.itemMenu.append(People_AddNew())
    PeopleList.itemMenu.append(balt.Tank_Delete())
    PeopleList.itemMenu.append(People_Export())

#------------------------------------------------------------------------------
def InitSettingsLinks():
    """Initialize settings menu."""
    SettingsMenu = BashStatusBar.SettingsMenu
    #--User settings
    SettingsMenu.append(Settings_BackupSettings())
    SettingsMenu.append(Settings_RestoreSettings())
    SettingsMenu.append(Settings_SaveSettings())
    #--OBSE Dll info
    SettingsMenu.append(SeparatorLink())
    SettingsMenu.append(Settings_ExportDllInfo())
    SettingsMenu.append(Settings_ImportDllInfo())
    #--Color config
    SettingsMenu.append(SeparatorLink())
    SettingsMenu.append(Settings_Colors())
    if True:
        tabsMenu = MenuLink(_(u'Tabs'))
        for key in bosh.settings['bash.tabs.order']:
            canDisable = bool(key != 'Mods')
            tabsMenu.links.append(Tab_Link(key,canDisable))
        SettingsMenu.append(tabsMenu)
    #--StatusBar
    if True:
        sbMenu = MenuLink(_(u'Status bar'))
        #--Icon size
        if True:
            sizeMenu = MenuLink(_(u'Icon size'))
            for size in (16,24,32):
                sizeMenu.links.append(Settings_IconSize(size))
            sbMenu.links.append(sizeMenu)
        sbMenu.links.append(Settings_UnHideButtons())
        sbMenu.links.append(Settings_StatusBar_ShowVersions())
        SettingsMenu.append(sbMenu)
    SettingsMenu.append(Settings_Languages())
    SettingsMenu.append(Settings_PluginEncodings())
    SettingsMenu.append(Settings_Games())
    SettingsMenu.append(SeparatorLink())
    SettingsMenu.append(Settings_UseAltName())
    SettingsMenu.append(Settings_Deprint())
    SettingsMenu.append(Settings_DumpTranslator())
    SettingsMenu.append(Settings_UAC())

def InitLinks():
    """Call other link initializers."""
    InitStatusBar()
    InitSettingsLinks()
    InitMasterLinks()
    InitInstallerLinks()
    InitINILinks()
    InitModLinks()
    InitSaveLinks()
    InitScreenLinks()
    InitMessageLinks()
    InitPeopleLinks()
    #InitBSALinks()
