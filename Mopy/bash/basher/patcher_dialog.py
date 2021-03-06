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
"""Patch dialog"""
import StringIO
import copy
import re
import time
import wx # TODO(ut): de wx
from ..balt import button, staticText, vSizer, hSizer, spacer, Link
from ..bolt import UncodedError, SubProgress, GPath, CancelError, BoltError, \
    SkipError, deprint, Path
from . import SetUAC, Resources
from .. import bosh, bolt, balt

modList = None

class PatchDialog(balt.Dialog):
    """Bash Patch update dialog."""
    patchers = []       #--All patchers. These are copied as needed.
    CBash_patchers = [] #--All patchers (CBash mode).  These are copied as needed.

    def __init__(self,parent,patchInfo,doCBash=None,importConfig=True):
        self.parent = parent
        if (doCBash or doCBash is None) and bosh.settings['bash.CBashEnabled']:
            doCBash = True
        else:
            doCBash = False
        self.doCBash = doCBash
        title = _(u'Update ') + patchInfo.name.s + [u'', u' (CBash)'][doCBash]
        size = balt.sizes.get(self.__class__.__name__, (500,600))
        super(PatchDialog, self).__init__(parent, title=title, size=size)
        self.SetSizeHints(400,300)
        #--Data
        groupOrder = dict([(group,index) for index,group in
            enumerate((_(u'General'),_(u'Importers'),_(u'Tweakers'),_(u'Special')))])
        patchConfigs = bosh.modInfos.table.getItem(patchInfo.name,'bash.patch.configs',{})
        # If the patch config isn't from the same mode (CBash/Python), try converting
        # it over to the current mode
        configIsCBash = bosh.CBash_PatchFile.configIsCBash(patchConfigs)
        if configIsCBash != self.doCBash:
            if importConfig:
                patchConfigs = self.ConvertConfig(patchConfigs)
            else:
                patchConfigs = {}
        isFirstLoad = 0 == len(patchConfigs)
        self.patchInfo = patchInfo
        if doCBash:
            self.patchers = [copy.deepcopy(patcher) for patcher in PatchDialog.CBash_patchers]
        else:
            self.patchers = [copy.deepcopy(patcher) for patcher in PatchDialog.patchers]
        self.patchers.sort(key=lambda a: a.__class__.name)
        self.patchers.sort(key=lambda a: groupOrder[a.__class__.group])
        for patcher in self.patchers:
            patcher.getConfig(patchConfigs) #--Will set patcher.isEnabled
            if u'UNDEFINED' in (patcher.__class__.group, patcher.__class__.group):
                raise UncodedError(u'Name or group not defined for: %s' % patcher.__class__.__name__)
            patcher.SetCallbackFns(self._CheckPatcher, self._BoldPatcher)
            patcher.SetIsFirstLoad(isFirstLoad)
        self.currentPatcher = None
        patcherNames = [patcher.getName() for patcher in self.patchers]
        #--GUI elements
        self.gExecute = button(self,id=wx.ID_OK,label=_(u'Build Patch'),onClick=self.Execute)
        SetUAC(self.gExecute)
        self.gSelectAll = button(self,id=wx.wx.ID_SELECTALL,label=_(u'Select All'),onClick=self.SelectAll)
        self.gDeselectAll = button(self,id=wx.wx.ID_SELECTALL,label=_(u'Deselect All'),onClick=self.DeselectAll)
        cancelButton = button(self,id=wx.ID_CANCEL,label=_(u'Cancel'))
        self.gPatchers = balt.listBox(self, choices=patcherNames,
                                      isSingle=True, kind='checklist')
        self.gExportConfig = button(self,id=wx.ID_SAVEAS,label=_(u'Export'),onClick=self.ExportConfig)
        self.gImportConfig = button(self,id=wx.ID_OPEN,label=_(u'Import'),onClick=self.ImportConfig)
        self.gRevertConfig = button(self,id=wx.ID_REVERT_TO_SAVED,label=_(u'Revert To Saved'),onClick=self.RevertConfig)
        self.gRevertToDefault = button(self,id=wx.ID_REVERT,label=_(u'Revert To Default'),onClick=self.DefaultConfig)
        for index,patcher in enumerate(self.patchers):
            self.gPatchers.Check(index,patcher.isEnabled)
        self.defaultTipText = _(u'Items that are new since the last time this patch was built are displayed in bold')
        self.gTipText = staticText(self,self.defaultTipText)
        #--Events
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.gPatchers.Bind(wx.EVT_LISTBOX, self.OnSelect)
        self.gPatchers.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        self.gPatchers.Bind(wx.EVT_MOTION,self.OnMouse)
        self.gPatchers.Bind(wx.EVT_LEAVE_WINDOW,self.OnMouse)
        self.gPatchers.Bind(wx.EVT_CHAR,self.OnChar)
        self.mouseItem = -1
        #--Layout
        self.gConfigSizer = gConfigSizer = vSizer()
        sizer = vSizer(
            (hSizer(
                (self.gPatchers,0,wx.EXPAND),
                (self.gConfigSizer,1,wx.EXPAND|wx.LEFT,4),
                ),1,wx.EXPAND|wx.ALL,4),
            (self.gTipText,0,wx.EXPAND|wx.ALL^wx.TOP,4),
            (wx.StaticLine(self),0,wx.EXPAND|wx.BOTTOM,4),
            (hSizer(
                spacer,
                (self.gExportConfig,0,wx.LEFT,4),
                (self.gImportConfig,0,wx.LEFT,4),
                (self.gRevertConfig,0,wx.LEFT,4),
                (self.gRevertToDefault,0,wx.LEFT,4),
                ),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,4),
            (hSizer(
                spacer,
                self.gExecute,
                (self.gSelectAll,0,wx.LEFT,4),
                (self.gDeselectAll,0,wx.LEFT,4),
                (cancelButton,0,wx.LEFT,4),
                ),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,4)
            )
        self.SetSizer(sizer)
        self.SetIcons(Resources.bashMonkey)
        #--Patcher panels
        for patcher in self.patchers:
            gConfigPanel = patcher.GetConfigPanel(self,gConfigSizer,self.gTipText)
            gConfigSizer.Show(gConfigPanel,False)
        self.gPatchers.Select(1)
        self.ShowPatcher(self.patchers[1])
        self.SetOkEnable()

    #--Core -------------------------------
    def SetOkEnable(self):
        """Sets enable state for Ok button."""
        for patcher in self.patchers:
            if patcher.isEnabled:
                return self.gExecute.Enable(True)
        self.gExecute.Enable(False)

    def ShowPatcher(self,patcher):
        """Show patcher panel."""
        gConfigSizer = self.gConfigSizer
        if patcher == self.currentPatcher: return
        if self.currentPatcher is not None:
            gConfigSizer.Show(self.currentPatcher.gConfigPanel,False)
        gConfigPanel = patcher.GetConfigPanel(self,gConfigSizer,self.gTipText)
        gConfigSizer.Show(gConfigPanel,True)
        self.Layout()
        patcher.Layout()
        self.currentPatcher = patcher

    def Execute(self,event=None):
        """Do the patch."""
        self.EndModalOK()
        patchName = self.patchInfo.name
        progress = balt.Progress(patchName.s,(u' '*60+u'\n'), abort=True)
        ###Remove from Bash after CBash integrated
        patchFile = None
        if self.doCBash: # TODO(ut): factor out duplicated code in this if/else!!
            try:
                from datetime import timedelta
                timer1 = time.clock()
                fullName = self.patchInfo.getPath().tail
                #--Save configs
                patchConfigs = {'ImportedMods':set()}
                for patcher in self.patchers:
                    patcher.saveConfig(patchConfigs)
                bosh.modInfos.table.setItem(patchName,'bash.patch.configs',patchConfigs)
                #--Do it
                log = bolt.LogFile(StringIO.StringIO())
                patchers = [patcher for patcher in self.patchers if patcher.isEnabled]

                patchFile = bosh.CBash_PatchFile(patchName,patchers)
                #try to speed this up!
                patchFile.initData(SubProgress(progress,0,0.1))
                #try to speed this up!
                patchFile.buildPatch(SubProgress(progress,0.1,0.9))
                #no speeding needed/really possible (less than 1/4 second even with large LO)
                patchFile.buildPatchLog(patchName,log,SubProgress(progress,0.95,0.99))
                #--Save
                progress.setCancel(False)
                progress(1.0,patchName.s+u'\n'+_(u'Saving...'))
                patchFile.save()
                patchTime = fullName.mtime
                try:
                    patchName.untemp()
                except WindowsError, werr:
                    if werr.winerror != 32: raise
                    while balt.askYes(self,(_(u'Bash encountered an error when renaming %s to %s.')
                                            + u'\n\n' +
                                            _(u'The file is in use by another process such as TES4Edit.')
                                            + u'\n' +
                                            _(u'Please close the other program that is accessing %s.')
                                            + u'\n\n' +
                                            _(u'Try again?')) % (patchName.temp.s, patchName.s, patchName.s),
                                      _(u'Bash Patch - Save Error')):
                        try:
                            patchName.untemp()
                        except WindowsError, werr:
                            continue
                        break
                    else:
                        raise
                patchName.mtime = patchTime
                #--Cleanup
                self.patchInfo.refresh()
                modList.RefreshUI(patchName)
                #--Done
                progress.Destroy()
                timer2 = time.clock()
                #--Readme and log
                log.setHeader(None)
                log(u'{{CSS:wtxt_sand_small.css}}')
                logValue = log.out.getvalue()
                log.out.close()
                timerString = unicode(timedelta(seconds=round(timer2 - timer1, 3))).rstrip(u'0')
                logValue = re.sub(u'TIMEPLACEHOLDER', timerString, logValue, 1)
                readme = bosh.modInfos.dir.join(u'Docs',patchName.sroot+u'.txt')
                with readme.open('w',encoding='utf-8') as file:
                    file.write(logValue)
                bosh.modInfos.table.setItem(patchName,'doc',readme)
                #--Convert log/readme to wtxt and show log
                docsDir = bosh.settings.get('balt.WryeLog.cssDir', GPath(u'')) #bosh.modInfos.dir.join(u'Docs')
                bolt.WryeText.genHtml(readme,None,docsDir)
                balt.playSound(self.parent,bosh.inisettings['SoundSuccess'].s)
                balt.showWryeLog(self.parent,readme.root+u'.html',patchName.s,icons=Resources.bashBlue)
                #--Select?
                message = _(u'Activate %s?') % patchName.s
                if bosh.inisettings['PromptActivateBashedPatch'] \
                         and (bosh.modInfos.isSelected(patchName) or
                         balt.askYes(self.parent,message,patchName.s)):
                    try:
                        oldFiles = bosh.modInfos.ordered[:]
                        bosh.modInfos.select(patchName)
                        changedFiles = bolt.listSubtract(bosh.modInfos.ordered,oldFiles)
                        if len(changedFiles) > 1:
                            Link.Frame.GetStatusBar().SetText(_(u'Masters Activated: ') + unicode(len(changedFiles)-1))
                        bosh.modInfos[patchName].setGhost(False)
                        bosh.modInfos.refreshInfoLists()
                    except bosh.PluginsFullError:
                        balt.showError(self,
                            _(u'Unable to add mod %s because load list is full.')
                            % patchName.s)
                    modList.RefreshUI()
            except bolt.FileEditError, error:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                balt.showError(self,u'%s'%error,_(u'File Edit Error'))
            except CancelError:
                pass
            except BoltError, error:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                balt.showError(self,u'%s'%error,_(u'Processing Error'))
            except:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                raise
            finally:
                try:
                    patchFile.Current.Close()
                except:
                    pass
                progress.Destroy()
        else:
            try:
                from datetime import timedelta
                timer1 = time.clock()
                #--Save configs
                patchConfigs = {'ImportedMods':set()}
                for patcher in self.patchers:
                    patcher.saveConfig(patchConfigs)
                bosh.modInfos.table.setItem(patchName,'bash.patch.configs',patchConfigs)
                #--Do it
                log = bolt.LogFile(StringIO.StringIO())
                nullProgress = bolt.Progress()
                patchers = [patcher for patcher in self.patchers if patcher.isEnabled]
                patchFile = bosh.PatchFile(self.patchInfo,patchers)
                patchFile.initData(SubProgress(progress,0,0.1)) #try to speed this up!
                patchFile.initFactories(SubProgress(progress,0.1,0.2)) #no speeding needed/really possible (less than 1/4 second even with large LO)
                patchFile.scanLoadMods(SubProgress(progress,0.2,0.8)) #try to speed this up!
                patchFile.buildPatch(log,SubProgress(progress,0.8,0.9))#no speeding needed/really possible (less than 1/4 second even with large LO)
                #--Save
                progress.setCancel(False)
                progress(0.9,patchName.s+u'\n'+_(u'Saving...'))
                message = (_(u'Bash encountered and error when saving %(patchName)s.')
                           + u'\n\n' +
                           _(u'Either Bash needs Administrator Privileges to save the file, or the file is in use by another process such as TES4Edit.')
                           + u'\n' +
                           _(u'Please close any program that is accessing %(patchName)s, and provide Administrator Privileges if prompted to do so.')
                           + u'\n\n' +
                           _(u'Try again?')) % {'patchName':patchName.s}
                while True:
                    try:
                        patchFile.safeSave()
                    except (CancelError,SkipError,WindowsError) as error:
                        if isinstance(error,WindowsError) and error.winerror != 32:
                            raise
                        if balt.askYes(self,message,_(u'Bash Patch - Save Error')):
                            continue
                        raise CancelError
                    break

                #--Cleanup
                self.patchInfo.refresh()
                modList.RefreshUI(patchName)
                #--Done
                progress.Destroy()
                timer2 = time.clock()
                #--Readme and log
                log.setHeader(None)
                log(u'{{CSS:wtxt_sand_small.css}}')
                logValue = log.out.getvalue()
                log.out.close()
                timerString = unicode(timedelta(seconds=round(timer2 - timer1, 3))).rstrip(u'0')
                logValue = re.sub(u'TIMEPLACEHOLDER', timerString, logValue, 1)
                readme = bosh.modInfos.dir.join(u'Docs',patchName.sroot+u'.txt')
                tempReadmeDir = Path.tempDir(u'WryeBash_').join(u'Docs')
                tempReadme = tempReadmeDir.join(patchName.sroot+u'.txt')
                #--Write log/readme to temp dir first
                with tempReadme.open('w',encoding='utf-8-sig') as file:
                    file.write(logValue)
                #--Convert log/readmeto wtxt
                docsDir = bosh.settings.get('balt.WryeLog.cssDir', GPath(u''))
                bolt.WryeText.genHtml(tempReadme,None,docsDir)
                #--Try moving temp log/readme to Docs dir
                try:
                    balt.shellMove(tempReadmeDir,bosh.dirs['mods'],self,False,False,False)
                except (CancelError,SkipError):
                    # User didn't allow UAC, move to My Games directoy instead
                    balt.shellMove([tempReadme,tempReadme.root+u'.html'],bosh.dirs['saveBase'],self,False,False,False)
                    readme = bosh.dirs['saveBase'].join(readme.tail)
                #finally:
                #    tempReadmeDir.head.rmtree(safety=tempReadmeDir.head.stail)
                bosh.modInfos.table.setItem(patchName,'doc',readme)
                #--Convert log/readme to wtxt and show log
                balt.playSound(self.parent,bosh.inisettings['SoundSuccess'].s)
                balt.showWryeLog(self.parent,readme.root+u'.html',patchName.s,icons=Resources.bashBlue)
                #--Select?
                message = _(u'Activate %s?') % patchName.s
                if bosh.inisettings['PromptActivateBashedPatch'] \
                         and (bosh.modInfos.isSelected(patchName) or
                          balt.askYes(self.parent,message,patchName.s)):
                    try:
                        # Note to the regular WB devs:
                        #  The bashed patch wasn't activating when it had been manually deleting. So, on
                        #   startup, WB would create a new one, but something, somewhere (libloadorder?) wasn't
                        #   registering this so when this: bosh.modInfos.select(patchName) executed, bash
                        #   couldn't actually find anything to execute. This fix really belongs somewhere else
                        #   (after the patch is recreated?), but I don't know where it goes, so I'm sticking it
                        #   here until one of you come back or I find a better place.
                        bosh.modInfos.plugins.refresh(True)
                        oldFiles = bosh.modInfos.ordered[:]
                        bosh.modInfos.select(patchName)
                        changedFiles = bolt.listSubtract(bosh.modInfos.ordered,oldFiles)
                        if len(changedFiles) > 1:
                            Link.Frame.GetStatusBar().SetText(_(u'Masters Activated: ') + unicode(len(changedFiles)-1))
                        bosh.modInfos[patchName].setGhost(False)
                        bosh.modInfos.refreshInfoLists()
                    except bosh.PluginsFullError:
                        balt.showError(self,
                            _(u'Unable to add mod %s because load list is full.')
                            % patchName.s)
                    modList.RefreshUI()
            except bolt.FileEditError, error:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                balt.showError(self,u'%s'%error,_(u'File Edit Error'))
            except CancelError:
                pass
            except BoltError, error:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                balt.showError(self,u'%s'%error,_(u'Processing Error'))
            except:
                balt.playSound(self.parent,bosh.inisettings['SoundError'].s)
                raise
            finally:
                progress.Destroy()

    def SaveConfig(self,event=None):
        """Save the configuration"""
        patchName = self.patchInfo.name
        patchConfigs = {'ImportedMods':set()}
        for patcher in self.patchers:
            patcher.saveConfig(patchConfigs)
        bosh.modInfos.table.setItem(patchName,'bash.patch.configs',patchConfigs)

    def ExportConfig(self,event=None):
        """Export the configuration to a user selected dat file."""
        patchName = self.patchInfo.name + _(u'_Configuration.dat')
        textDir = bosh.dirs['patches']
        textDir.makedirs()
        #--File dialog
        textPath = balt.askSave(self.parent,_(u'Export Bashed Patch configuration to:'),
                                textDir,patchName, u'*Configuration.dat')
        if not textPath: return
        pklPath = textPath+u'.pkl'
        table = bolt.Table(bosh.PickleDict(textPath, pklPath))
        patchConfigs = {'ImportedMods':set()}
        for patcher in self.patchers:
            patcher.saveConfig(patchConfigs)
        table.setItem(GPath(u'Saved Bashed Patch Configuration (%s)' % ([u'Python',u'CBash'][self.doCBash])),'bash.patch.configs',patchConfigs)
        table.save()

    def ImportConfig(self,event=None):
        """Import the configuration to a user selected dat file."""
        patchName = self.patchInfo.name + _(u'_Configuration.dat')
        textDir = bosh.dirs['patches']
        textDir.makedirs()
        #--File dialog
        textPath = balt.askOpen(self.parent,_(u'Import Bashed Patch configuration from:'),textDir,patchName, u'*.dat',mustExist=True)
        if not textPath: return
        pklPath = textPath+u'.pkl'
        table = bolt.Table(bosh.PickleDict(
            textPath, pklPath))
        #try the current Bashed Patch mode.
        patchConfigs = table.getItem(GPath(u'Saved Bashed Patch Configuration (%s)' % ([u'Python',u'CBash'][self.doCBash])),'bash.patch.configs',{})
        if not patchConfigs: #try the old format:
            patchConfigs = table.getItem(GPath(u'Saved Bashed Patch Configuration'),'bash.patch.configs',{})
            if patchConfigs:
                configIsCBash = bosh.CBash_PatchFile.configIsCBash(patchConfigs)
                if configIsCBash != self.doCBash:
                    patchConfigs = self.UpdateConfig(patchConfigs)
            else:   #try the non-current Bashed Patch mode:
                patchConfigs = table.getItem(GPath(u'Saved Bashed Patch Configuration (%s)' % ([u'CBash',u'Python'][self.doCBash])),'bash.patch.configs',{})
                if patchConfigs:
                    patchConfigs = self.UpdateConfig(patchConfigs)
        if patchConfigs is None:
            patchConfigs = {}
        for index,patcher in enumerate(self.patchers):
            patcher.SetIsFirstLoad(False)
            patcher.getConfig(patchConfigs)
            self.gPatchers.Check(index,patcher.isEnabled)
            if hasattr(patcher, 'gList'):
                if patcher.getName() == 'Leveled Lists': continue #not handled yet!
                for index, item in enumerate(patcher.items):
                    try:
                        patcher.gList.Check(index,patcher.configChecks[item])
                    except KeyError: pass#deprint(_(u'item %s not in saved configs') % (item))
            if hasattr(patcher, 'gTweakList'):
                for index, item in enumerate(patcher.tweaks):
                    try:
                        patcher.gTweakList.Check(index,item.isEnabled)
                        patcher.gTweakList.SetString(index,item.getListLabel())
                    except: deprint(_(u'item %s not in saved configs') % item)
        self.SetOkEnable()

    def UpdateConfig(self,patchConfigs,event=None):
        if not balt.askYes(self.parent,
            _(u"Wrye Bash detects that the selected file was saved in Bash's %s mode, do you want Wrye Bash to attempt to adjust the configuration on import to work with %s mode (Good chance there will be a few mistakes)? (Otherwise this import will have no effect.)")
                % ([u'CBash',u'Python'][self.doCBash],
                   [u'Python',u'CBash'][self.doCBash])):
            return
        if self.doCBash:
            bosh.PatchFile.patchTime = bosh.CBash_PatchFile.patchTime
            bosh.PatchFile.patchName = bosh.CBash_PatchFile.patchName
        else:
            bosh.CBash_PatchFile.patchTime = bosh.PatchFile.patchTime
            bosh.CBash_PatchFile.patchName = bosh.PatchFile.patchName
        return self.ConvertConfig(patchConfigs)

    def ConvertConfig(self,patchConfigs):
        newConfig = {}
        for key in patchConfigs:
            if key in otherPatcherDict:
                newConfig[otherPatcherDict[key]] = patchConfigs[key]
            else:
                newConfig[key] = patchConfigs[key]
        return newConfig

    def RevertConfig(self,event=None):
        """Revert configuration back to saved"""
        patchConfigs = bosh.modInfos.table.getItem(self.patchInfo.name,'bash.patch.configs',{})
        if bosh.CBash_PatchFile.configIsCBash(patchConfigs) and not self.doCBash:
            patchConfigs = self.ConvertConfig(patchConfigs)
        for index,patcher in enumerate(self.patchers):
            patcher.SetIsFirstLoad(False)
            patcher.getConfig(patchConfigs)
            self.gPatchers.Check(index,patcher.isEnabled)
            if hasattr(patcher, 'gList'):
                if patcher.getName() == 'Leveled Lists': continue #not handled yet!
                for index, item in enumerate(patcher.items):
                    try: patcher.gList.Check(index,patcher.configChecks[item])
                    except Exception, err: deprint(_(u'Error reverting Bashed patch configuration (error is: %s). Item %s skipped.') % (err,item))
            if hasattr(patcher, 'gTweakList'):
                for index, item in enumerate(patcher.tweaks):
                    try:
                        patcher.gTweakList.Check(index,item.isEnabled)
                        patcher.gTweakList.SetString(index,item.getListLabel())
                    except Exception, err: deprint(_(u'Error reverting Bashed patch configuration (error is: %s). Item %s skipped.') % (err,item))
        self.SetOkEnable()

    def DefaultConfig(self,event=None):
        """Revert configuration back to default"""
        patchConfigs = {}
        for index,patcher in enumerate(self.patchers):
            patcher.SetIsFirstLoad(True)
            patcher.getConfig(patchConfigs)
            self.gPatchers.Check(index,patcher.isEnabled)
            if hasattr(patcher, 'gList'):
                patcher.SetItems(patcher.getAutoItems())
            if hasattr(patcher, 'gTweakList'):
                for index, item in enumerate(patcher.tweaks):
                    try:
                        patcher.gTweakList.Check(index,item.isEnabled)
                        patcher.gTweakList.SetString(index,item.getListLabel())
                    except Exception, err: deprint(_(u'Error reverting Bashed patch configuration (error is: %s). Item %s skipped.') % (err,item))
        self.SetOkEnable()

    def SelectAll(self,event=None):
        """Select all patchers and entries in patchers with child entries."""
        for index,patcher in enumerate(self.patchers):
            self.gPatchers.Check(index,True)
            patcher.isEnabled = True
            if hasattr(patcher, 'gList'):
                if patcher.getName() == 'Leveled Lists': continue
                for index, item in enumerate(patcher.items):
                    patcher.gList.Check(index,True)
                    patcher.configChecks[item] = True
            if hasattr(patcher, 'gTweakList'):
                for index, item in enumerate(patcher.tweaks):
                    patcher.gTweakList.Check(index,True)
                    item.isEnabled = True
            self.gExecute.Enable(True)

    def DeselectAll(self,event=None):
        """Deselect all patchers and entries in patchers with child entries."""
        for index,patcher in enumerate(self.patchers):
            self.gPatchers.Check(index,False)
            patcher.isEnabled = False
            if patcher.getName() in [_(u'Leveled Lists'),_(u"Alias Mod Names")]: continue # special case that one.
            if hasattr(patcher, 'gList'):
                patcher.gList.SetChecked([])
                patcher.OnListCheck()
            if hasattr(patcher, 'gTweakList'):
                patcher.gTweakList.SetChecked([])
        self.gExecute.Enable(False)

    #--GUI --------------------------------
    def OnSize(self,event):
        balt.sizes[self.__class__.__name__] = self.GetSizeTuple()
        self.Layout()
        self.currentPatcher.Layout()

    def OnSelect(self,event):
        """Responds to patchers list selection."""
        itemDex = event.GetSelection()
        self.ShowPatcher(self.patchers[itemDex])

    def _CheckPatcher(self,patcher):
        """Remotely enables a patcher.  Called from a particular patcher's OnCheck method."""
        index = self.patchers.index(patcher)
        self.gPatchers.Check(index)
        patcher.isEnabled = True
        self.SetOkEnable()

    def _BoldPatcher(self,patcher):
        """Set the patcher label to bold font.  Called from a patcher when it realizes it has something new in its list"""
        index = self.patchers.index(patcher)
        font = self.gPatchers.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.gPatchers.SetItemFont(index, font)

    def OnCheck(self,event):
        """Toggle patcher activity state."""
        index = event.GetSelection()
        patcher = self.patchers[index]
        patcher.isEnabled = self.gPatchers.IsChecked(index)
        self.gPatchers.SetSelection(index)
        self.ShowPatcher(patcher)
        self.SetOkEnable()

    def OnMouse(self,event):
        """Check mouse motion to detect right click event."""
        if event.Moving():
            mouseItem = (event.m_y/self.gPatchers.GetItemHeight() +
                self.gPatchers.GetScrollPos(wx.VERTICAL))
            if mouseItem != self.mouseItem:
                self.mouseItem = mouseItem
                self.MouseEnteredItem(mouseItem)
        elif event.Leaving():
            self.gTipText.SetLabel(self.defaultTipText)
            self.mouseItem = -1
        event.Skip()

    def MouseEnteredItem(self,item):
        """Show tip text when changing item."""
        #--Following isn't displaying correctly.
        if item < len(self.patchers):
            patcherClass = self.patchers[item].__class__
            tip = patcherClass.tip or re.sub(ur'\..*',u'.',patcherClass.text.split(u'\n')[0],flags=re.U)
            self.gTipText.SetLabel(tip)
        else:
            self.gTipText.SetLabel(self.defaultTipText)

    def OnChar(self,event):
        """Keyboard input to the patchers list box"""
        if event.GetKeyCode() == 1 and event.CmdDown(): # Ctrl+'A'
            patcher = self.currentPatcher
            if patcher is not None:
                if event.ShiftDown():
                    patcher.DeselectAll()
                else:
                    patcher.SelectAll()
                return
        event.Skip()

# Used in ConvertConfig to convert between C and P *gui* patchers config - so
# it belongs with gui_patchers (and not with patchers/ package). Still a hack
otherPatcherDict = {
    'AliasesPatcher' : 'CBash_AliasesPatcher',
    'AssortedTweaker' : 'CBash_AssortedTweaker',
    'PatchMerger' : 'CBash_PatchMerger',
    'KFFZPatcher' : 'CBash_KFFZPatcher',
    'ActorImporter' : 'CBash_ActorImporter',
    'DeathItemPatcher' : 'CBash_DeathItemPatcher',
    'NPCAIPackagePatcher' : 'CBash_NPCAIPackagePatcher',
    'UpdateReferences' : 'CBash_UpdateReferences',
    'CellImporter' : 'CBash_CellImporter',
    'ClothesTweaker' : 'CBash_ClothesTweaker',
    'GmstTweaker' : 'CBash_GmstTweaker',
    'GraphicsPatcher' : 'CBash_GraphicsPatcher',
    'ImportFactions' : 'CBash_ImportFactions',
    'ImportInventory' : 'CBash_ImportInventory',
    'SpellsPatcher' : 'CBash_SpellsPatcher',
    'TweakActors' : 'CBash_TweakActors',
    'ImportRelations' : 'CBash_ImportRelations',
    'ImportScripts' : 'CBash_ImportScripts',
    'ImportActorsSpells' : 'CBash_ImportActorsSpells',
    'ListsMerger' : 'CBash_ListsMerger',
    'NamesPatcher' : 'CBash_NamesPatcher',
    'NamesTweaker' : 'CBash_NamesTweaker',
    'NpcFacePatcher' : 'CBash_NpcFacePatcher',
    'RacePatcher' : 'CBash_RacePatcher',
    'RoadImporter' : 'CBash_RoadImporter',
    'SoundPatcher' : 'CBash_SoundPatcher',
    'StatsPatcher' : 'CBash_StatsPatcher',
    'ContentsChecker' : 'CBash_ContentsChecker',
    'CBash_AliasesPatcher' : 'AliasesPatcher',
    'CBash_AssortedTweaker' : 'AssortedTweaker',
    'CBash_PatchMerger' : 'PatchMerger',
    'CBash_KFFZPatcher' : 'KFFZPatcher',
    'CBash_ActorImporter' : 'ActorImporter',
    'CBash_DeathItemPatcher' : 'DeathItemPatcher',
    'CBash_NPCAIPackagePatcher' : 'NPCAIPackagePatcher',
    'CBash_UpdateReferences' : 'UpdateReferences',
    'CBash_CellImporter' : 'CellImporter',
    'CBash_ClothesTweaker' : 'ClothesTweaker',
    'CBash_GmstTweaker' : 'GmstTweaker',
    'CBash_GraphicsPatcher' : 'GraphicsPatcher',
    'CBash_ImportFactions' : 'ImportFactions',
    'CBash_ImportInventory' : 'ImportInventory',
    'CBash_SpellsPatcher' : 'SpellsPatcher',
    'CBash_TweakActors' : 'TweakActors',
    'CBash_ImportRelations' : 'ImportRelations',
    'CBash_ImportScripts' : 'ImportScripts',
    'CBash_ImportActorsSpells' : 'ImportActorsSpells',
    'CBash_ListsMerger' : 'ListsMerger',
    'CBash_NamesPatcher' : 'NamesPatcher',
    'CBash_NamesTweaker' : 'NamesTweaker',
    'CBash_NpcFacePatcher' : 'NpcFacePatcher',
    'CBash_RacePatcher' : 'RacePatcher',
    'CBash_RoadImporter' : 'RoadImporter',
    'CBash_SoundPatcher' : 'SoundPatcher',
    'CBash_StatsPatcher' : 'StatsPatcher',
    'CBash_ContentsChecker' : 'ContentsChecker',
    }
