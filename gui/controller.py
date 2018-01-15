'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This module represents the statechart controller of BiBler.
It should be used as an API that a L{statechart<gui.statechart.BiBler_Statechart>}, a L{GUI<gui.MainWindow>} and an L{application<app_interface.IApplication>} can invoke.
'''

from statechart import BiBler_Statechart
from app_interface import EntryListColumn

#from app.entry import Entry

class ControllerData(object):
    """
    It encapsulates the state of the controller.
    The data that can be used by the controller and statechart.
    """
    def __init__(self):
        self.errorMsg = ""
        self.statusMsg = ""
        self.path = None
        self.bibtexFilepath = None
        self.importFormat = None
        self.exportFormat = None
        self.searchQuery = None
        self.entryList = None
        self.currentEntryId = None
        self.currentEntryBibTeX = None
        self.currentEntryHTML = None
        self.currentEntryDict = None
        self.currentEntryPaperURL = None
        self.sortColumn = None

class ControllerLogicException(Exception):
    """
    Exception that can be raised by the L{Controller}.
    """
    def __init__(self, msg):
        Exception.__init__(self, msg)

class Controller(object):
    """
    The statechart controller that defines the behavior of the GUI.
    It manages the communication between the statechart and the GUI.
    It also exposes an API for sending events to the statechart and an API of the functions the statechart can invoke,
    which is delegated to either the GUI or the application.
    @group Statechart events:
    *Clicked, preferencesChanged, textChangedInEditor, entryDeselected, entrySelected, exportFileSelected, importFileSelected, openFileSelected, saveFileSelected
    @group API to interface with Statechart:
    __sendAppOperationResult, __sendError, __sendEvent, isBibtexFileLoaded
    @group API to interface with Application:
    addEntry, currentEntryHasPaper, deleteEntry, duplicateEntry, getBibTeX, exportFile, getAllEntries, getDisplayedEntryCount, getEntryPaperURL, hasUndoableActionLeft, importFile, openFile, previewEntry, saveFile, search, sort, undo, updateEntry
    @group API to interface with GUI:
    addNewEntryRow, clearEditor, clearList, clearPreviewer, clearStatusBar, disable*, enable*, displayBibTexInEditor, displayEntries, isEntrySelected, openEntryPaper, popup*, previewEntryHTML, removeEntryRow, selectCurrentEntryRow, setDirtyTitle, setStatusMsg, unselectEntryRow, unsetDirtyTitle, updateSelectedEntryRow, updateStatusBar, updateStatusTotal
    @sort:
    __*, a*, b*, c*, d*, e*, f*, g*, h*, i*, m*, o*, p*, r*, s*, t*, u*
    """
    def __init__(self):
        self.GUI = None
        self.APP = None
        self.SC = BiBler_Statechart()
        self.data = ControllerData()
        
    def bindSC(self, statechart):
        """
        Attach a statechart to the controller.
        @type statechart: L{statechart}
        @param statechart: The statechart.
        """
        self.SC = statechart
        
    def bindGUI(self, gui):
        """
        Attach a GUI to the controller.
        @type gui: L{MainWindow}
        @param gui: The GUI.
        """
        self.GUI = gui
        
    def bindApp(self, application):
        """
        Attach an application to the controller.
        @type application: L{IApplication}
        @param application: The application.
        """
        self.APP = application
    
    def start(self):
        """
        Start the GUI, the application, and the statechart.
        Sends a C{start} event to the statechart. 
        """
        self.GUI.start()
        self.APP.start()
        self.SC.initModel()
        self.__sendEvent("start")
        
    def exit(self):
        """
        End the GUI and the application.
        Sends an C{exit} event to the statechart. 
        """
        self.APP.exit()
        self.GUI.exit()
        self.__sendEvent("exit")
                
    #####################
    # Events: interface from GUI to statechart
    #####################
    
    def __sendEvent(self, e):
        """
        Send event C{e} to the statechart.
        @type e: L{str}
        @param e: The event.
        """
        try:
            self.SC.event(e, self)
        except Exception, e:
            self.__sendError(e)
    
    def __sendError(self, ex):
        """
        Triggered if an exception occurred.
        Send an An C{error} event to the statechart.
        @type ex: L{Exception}
        @param ex: The exception.
        """
        msg = str(ex)
        if msg == '':
            msg = type(ex).__name__ 
        self.data.errorMsg = msg
        self.__sendEvent("error")
        #raise ex
    
    def __sendAppOperationResult(self, condition=lambda: True, ex=Exception('An error has occurred.')):
        """
        Send a C{success} event to the statechart if an operation it called was successful.
        Otherwise send a C{fail} event.
        @type condition: C{function}
        @param condition: A function that returns a L{bool}.
        @rtype: L{bool}
        @return: C{True} if C{condition()==True}, C{False} otherwise.
        """
        if condition():
            self.__sendEvent("success")
            return True
        else:
            self.__sendError(ex)
            return False

    def exitClicked(self):
        """
        Triggered when the GUI window was requested to be closed.
        Send an C{exitClicked} event to the statechart.
        """
        self.__sendEvent("exitClicked")
    
    def forceExitClicked(self):
        """
        Triggered when the GUI ignores to save pending changes and exit was requested.
        Send a C{forceExitClicked} event to the statechart.
        """
        self.__sendEvent("forceExitClicked")
    
    def openClicked(self):
        """
        Triggered when the GUI issues the open command.
        Send an C{openClicked} event to the statechart.
        """
        self.__sendEvent("openClicked")
    
    def openFileSelected(self, path, importFormat):
        """
        Triggered when a file to open is selected.
        Send a C{openFileSelected} event to the statechart.
        @type path: L{str}
        @param path: The path to a file. It is stored in the controller data.
        @type importFormat: L{settings.ImportFormat}
        @param importFormat: The format of the file. It is stored in the controller data.
        """
        self.data.bibtexFilepath = path
        self.data.importFormat = importFormat
        self.__sendEvent("openFileSelected")
    
    def saveClicked(self, exportFormat):
        """
        Triggered when the GUI issues the save command.
        Send a C{saveClicked} event to the statechart.
        @type exportFormat: L{settings.ExportFormat}
        @param exportFormat: The format to export to. It is stored in the controller data.
        """
        self.data.exportFormat = exportFormat
        self.__sendEvent("saveClicked")
    
    def saveAsClicked(self):
        """
        Triggered when the GUI issues the save as command.
        Send a C{saveAsClicked} event to the statechart.
        """
        self.__sendEvent("saveAsClicked")
    
    def saveFileSelected(self, path, exportFormat):
        """
        Triggered when a file to save to is selected.
        Send a C{saveFileSelected} event to the statechart.
        @type path: L{str}
        @param path: The path to a file. It is stored in the controller data.
        @type exportFormat: L{settings.ExportFormat}
        @param exportFormat: The format of the file. It is stored in the controller data.
        """
        self.data.bibtexFilepath = path
        self.data.exportFormat = exportFormat
        self.__sendEvent("saveFileSelected")
    
    def importClicked(self):
        """
        Triggered when the GUI issues the import command.
        Send a C{importClicked} event to the statechart.
        """
        self.__sendEvent("importClicked")
    
    def importFileSelected(self, path, importFormat):
        """
        Triggered when the GUI a file to import is selected.
        Send a C{importFileSelected} event to the statechart.
        @type path: L{str}
        @param path: The path to a file. It is stored in the controller data.
        @type importFormat: L{settings.ImportFormat}
        @param importFormat: The format of the file. It is stored in the controller data.
        """
        self.data.path = path
        self.data.importFormat = importFormat
        self.__sendEvent("importFileSelected")
        
    def exportClicked(self):
        """
        Triggered when the GUI issues the export command.
        Send a C{exportClicked} event to the statechart.
        """
        self.__sendEvent("exportClicked")
    
    def exportFileSelected(self, path, exportFormat):
        """
        Triggered when a file to export to is selected.
        Send a C{exportFileSelected} event to the statechart.
        @type path: L{str}
        @param path: The path to a file. It is stored in the controller data.
        @type exportFormat: L{settings.ExportFormat}
        @param exportFormat: The format of the file. It is stored in the controller data.
        """
        self.data.path = path
        self.data.exportFormat = exportFormat
        self.__sendEvent("exportFileSelected")
        
    def addClicked(self):
        """
        Triggered when the GUI issues the add command.
        Send a C{addClicked} event to the statechart.
        """
        self.__sendEvent("addClicked")
        
    def entrySelected(self, entryId):
        """
        Triggered when an entry is selected in the entry list.
        Send a C{entrySelected} event to the statechart.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry. It is stored in the controller data.
        """
        self.data.currentEntryId = entryId
        self.__sendEvent("entrySelected")
        
    def entryDeselected(self):
        """
        Triggered when no entry is selected in the entry list.
        Send a C{entryDeselected} event to the statechart.
        """
        self.data.currentEntryId = None
        self.__sendEvent("entryDeselected")
    
    def entryDoubleClicked(self, entryId):
        """
        Triggered when an entry is double-clicked in the entry list.
        Send a C{entryDoubleClicked} event to the statechart.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry. It is stored in the controller data.
        """
        self.data.currentEntryId = entryId
        self.__sendEvent("entryDoubleClicked")
        
    def updateButtonClicked(self, entryBibTeX):
        """
        Triggered when a reference must be updated.
        Send a C{updateButtonClicked} event to the statechart.
        @type entryBibTeX: L{str}
        @param entryBibTeX: The BibTeX representation of the reference. It is stored in the controller data.
        """
        self.data.currentEntryBibTeX = entryBibTeX
        self.__sendEvent("updateButtonClicked")
        
    def duplicateClicked(self):
        """
        Triggered when the GUI issues the duplicate command.
        Send a C{duplicateClicked} event to the statechart.
        """
        self.__sendEvent("duplicateClicked")
        
    def deleteClicked(self):
        """
        Triggered when the GUI issues the delete command.
        Send a C{deleteClicked} event to the statechart.
        """
        self.__sendEvent("deleteClicked")
    
    def textChangedInEditor(self, text):
        """
        Triggered when the text in the editor has changed.
        Send a C{textChangedInEditor} event to the statechart. It is stored in the controller data.
        @type text: L{str}
        @param text: The new text.
        """
        if text != '':
            self.__sendEvent("textChangedInEditor")
    
    def undoClicked(self):
        """
        Triggered when the GUI issues the undo command.
        Send a C{undoClicked} event to the statechart.
        """
        self.__sendEvent("undoClicked")
        
    def searchClicked(self):
        """
        Triggered when the GUI issues the search command.
        Send a C{searchClicked} event to the statechart.
        """
        self.__sendEvent("searchClicked")
    
    def filterClicked(self, query):
        """
        Triggered when the GUI issued the filter command.
        Send a C{filterClicked} event to the statechart.
        @type query: L{str}
        @param query: The search query. It is stored in the controller data.
        """
        self.data.searchQuery = query
        self.__sendEvent("filterClicked")
    
    def clearFilterClicked(self):
        """
        Triggered when the GUI issues the clear filter command.
        Send a C{clearFilterClicked} event to the statechart.
        """
        self.__sendEvent("clearFilterClicked")
        
    def preferencesClicked(self):
        """
        Triggered when the GUI issues the preferences command.
        Send a C{preferencesClicked} event to the statechart.
        """
        self.__sendEvent("preferencesClicked")
    
    def preferencesChanged(self):
        """
        Triggered when the preferences of the GUI have changed.
        Send a C{preferencesChanged} event to the statechart.
        """
        self.__sendEvent("preferencesChanged")
        
    def aboutClicked(self):
        """
        Triggered when the GUI issues the about command.
        Send a C{aboutClicked} event to the statechart.
        """
        self.__sendEvent("aboutClicked")
        
    def manualClicked(self):
        """
        Triggered when the GUI issues the user manual command.
        Send a C{manualClicked} event to the statechart.
        """
        self.__sendEvent("manualClicked")
        
    def cancelClicked(self):
        """
        Triggered when a cancel button is clicked.
        Send a C{cancelClicked} event to the statechart.
        """
        self.__sendEvent("cancelClicked")
        
    def colIdClicked(self):
        """
        Triggered when the Id column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.ID
        self.__sendEvent("colClicked")
        
    def colPaperClicked(self):
        """
        Triggered when the Paper column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.PAPER
        self.__sendEvent("colClicked")
        
    def colTypeClicked(self):
        """
        Triggered when the Type column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.TYPE
        self.__sendEvent("colClicked")
        
    def colAuthorClicked(self):
        """
        Triggered when the Author column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.AUTHOR
        self.__sendEvent("colClicked")
        
    def colTitleClicked(self):
        """
        Triggered when the Title column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.TITLE
        self.__sendEvent("colClicked")
        
    def colYearClicked(self):
        """
        Triggered when the Year column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.YEAR
        self.__sendEvent("colClicked")
        
    def colKeyClicked(self):
        """
        Triggered when the Key column header is clicked.
        Send a C{colClicked} event to the statechart.
        The corresponding column is stored in the controller data.
        """
        self.data.sortColumn = EntryListColumn.KEY
        self.__sendEvent("colClicked")
    
    #####################
    # Actions: Interface from statechart to APP
    #####################
    
    def openFile(self):
        """
        Import a BibTeX file from a selected path.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no file was selected, the import format is undefined,
        L{IApplication.importFile<gui.app_interface.IApplication.importFile>} raised an exception,
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        if self.data.bibtexFilepath is None:
            self.__sendError(ControllerLogicException('No file was selected.'))
        elif self.data.importFormat is None:
            self.__sendError(ControllerLogicException('Open format undefined.'))
        else:
            try:
                result = self.APP.openFile(self.data.bibtexFilepath)
                self.data.entryList = self.APP.getAllEntries()
                if not self.__sendAppOperationResult(lambda: result and self.data.entryList is not None,
                                                     ControllerLogicException('Open failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def saveFile(self):
        """
        Export a BibTeX file to a selected path.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no file was selected, the export format is undefined,
        or L{IApplication.exportFile<gui.app_interface.IApplication.exportFile>} raised an exception.
        """
        if self.data.bibtexFilepath is None:
            self.__sendError(ControllerLogicException('No file was selected.'))
        elif self.data.exportFormat is None:
            self.__sendError(ControllerLogicException('Save format undefined.'))
        else:
            try:
                result = self.APP.exportFile(self.data.bibtexFilepath, self.data.exportFormat)
                if not self.__sendAppOperationResult(lambda: result is not None,
                                                     ControllerLogicException('Save failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def importFile(self):
        """
        Import a file from a selected path in a given format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no file was selected, the import format is undefined,
        L{IApplication.importFile<gui.app_interface.IApplication.importFile>} raised an exception,
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        if self.data.path is None:
            self.__sendError(ControllerLogicException('Import path undefined.'))
        elif self.data.importFormat is None:
            self.__sendError(ControllerLogicException('Import format undefined.'))
        else:
            try:
                result = self.APP.importFile(self.data.path, self.data.importFormat)
                self.data.entryList = self.APP.getAllEntries()
                if not self.__sendAppOperationResult(lambda: result and self.data.entryList is not None,
                                                     ControllerLogicException('Import failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def exportFile(self):
        """
        Export a file to a selected path in a given format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no file was selected, the export format is undefined,
        or L{IApplication.exportFile<gui.app_interface.IApplication.exportFile>} raised an exception.
        """
        if self.data.path is None:
            self.__sendError(ControllerLogicException('Export path undefined.'))
        elif self.data.exportFormat is None:
            self.__sendError(ControllerLogicException('Export format undefined.'))
        else:
            try:
                result = self.APP.exportFile(self.data.path, self.data.exportFormat)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Export failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def addEntry(self):
        """
        Add an entry from its BibTeX format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if
        L{IApplication.addEntry<gui.app_interface.IApplication.addEntry>} raised an exception,
        or L{IApplication.getEntry<gui.app_interface.IApplication.getEntry>} raised an exception,
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        try:
            self.data.currentEntryId = self.APP.addEntry(None)
            self.data.currentEntryDict = self.APP.getEntry(self.data.currentEntryId)
            self.data.entryList = self.APP.getAllEntries()
            if not self.__sendAppOperationResult(lambda: self.data.currentEntryId is not None \
                                                         and self.data.currentEntryDict is not None \
                                                         and self.data.entryList is not None,
                                                 ControllerLogicException('Add failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def duplicateEntry(self):
        """
        Duplicate the selected entry.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected
        L{IApplication.duplicateEntry<gui.app_interface.IApplication.duplicateEntry>} raised an exception,
        L{IApplication.getEntry<gui.app_interface.IApplication.getEntry>} raised an exception,
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        else:
            try:
                self.data.currentEntryId = self.APP.duplicateEntry(self.data.currentEntryId)
                self.data.currentEntryDict = self.APP.getEntry(self.data.currentEntryId)
                self.data.entryList = self.APP.getAllEntries()
                if not self.__sendAppOperationResult(lambda: self.data.currentEntryId is not None \
                                                             and self.data.currentEntryDict is not None \
                                                             and self.data.entryList is not None,
                                                     ControllerLogicException('Duplicate failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def updateEntry(self):
        """
        Update the selected entry from its BibTeX format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected, the entry was not converted to BibTeX format,
        L{IApplication.getEntry<gui.app_interface.IApplication.getEntry>} raised an exception,
        or L{IApplication.updateEntry<gui.app_interface.IApplication.updateEntry>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        elif self.data.currentEntryBibTeX is None:
            self.__sendError(ControllerLogicException('Entry must be converted to BibTeX format.'))
        else:
            try:
                result = self.APP.updateEntry(self.data.currentEntryId, self.data.currentEntryBibTeX)
                self.data.currentEntryDict = self.APP.getEntry(self.data.currentEntryId)
                if not self.__sendAppOperationResult(lambda: result and self.data.currentEntryDict is not None,
                                                     ControllerLogicException('Update failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def deleteEntry(self):
        """
        Delete the selected entry.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected
        L{IApplication.deleteEntry<gui.app_interface.IApplication.deleteEntry>} raised an exception,
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        else:
            try:
                result = self.APP.deleteEntry(self.data.currentEntryId)
                self.data.entryList = self.APP.getAllEntries()
                if not self.__sendAppOperationResult(lambda: result and self.data.entryList is not None,
                                                     ControllerLogicException('Delete failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def previewEntry(self):
        """
        Preview the selected entry in the preferred style.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected
        or L{IApplication.previewEntry<gui.app_interface.IApplication.previewEntry>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        else:
            try:
                self.data.currentEntryHTML = self.APP.previewEntry(self.data.currentEntryId)
                if not self.__sendAppOperationResult(lambda: self.data.currentEntryHTML is not None,
                                                     ControllerLogicException('Preview failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def search(self):
        """
        Search for entries that satisfy the query provided.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no search query was provided
        or L{IApplication.search<gui.app_interface.IApplication.search>} raised an exception.
        """
        if self.data.searchQuery is None:
            self.__sendError(ControllerLogicException('Search query not found.'))
        else:
            try:
                result = self.APP.search(self.data.searchQuery)
                self.data.entryList = self.APP.getSearchResult()
                if not self.__sendAppOperationResult(lambda: result >= 0 and self.data.entryList is not None,
                                                     ControllerLogicException('Search failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def sort(self):
        """
        Sort all entries with respect to the field corresponding to the selected column.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no column was selected
        or L{IApplication.sort<gui.app_interface.IApplication.sort>} raised an exception.
        """
        if self.data.sortColumn is None:
            self.__sendError(ControllerLogicException('No column was selected.'))
        else:
            try:
                result = self.APP.sort(self.data.sortColumn)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Sort failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def undo(self):
        """
        Undo the last action performed.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if
        or L{IApplication.undo<gui.app_interface.IApplication.undo>} raised an exception.
        """
        try:
            self.APP.undo()
            if not self.__sendAppOperationResult(ex=ControllerLogicException('Undo failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def getEntryPaperURL(self):
        """
        Get the URL of the paper of the selected entry.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected
        or L{IApplication.sort<gui.app_interface.IApplication.sort>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        else:
            try:
                self.data.currentEntryPaperURL = self.APP.getEntryPaperURL(self.data.currentEntryId)
                if self.data.currentEntryPaperURL == '':
                    self.data.currentEntryPaperURL = None
                if not self.__sendAppOperationResult(ex=ControllerLogicException('Failed searching for paper.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def currentEntryHasPaper(self):
        """
        Verify the selected entry has a paper.
        @rtype: L{bool}
        @return: C{True} if there is a paper, C{False} otherwise.
        """
        return self.data.currentEntryPaperURL is not None
    
    def hasUndoableActionLeft(self):
        """
        Verify if there is any action to undo.
        
        An C{error} event is sent to the statechart if
        L{IApplication.hasUndoableActionLeft<gui.app_interface.IApplication.hasUndoableActionLeft>} raised an exception.
        @rtype: L{bool}
        @return: C{True} if there is an action to undo, C{False} otherwise.
        """
        try:
            return self.APP.hasUndoableActionLeft()
        except Exception, e:
            self.__sendError(e)
    
    def getBibTeX(self):
        """
        Convert the selected entry to its BibTeX format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was selected
        or L{IApplication.getBibTeX<gui.app_interface.IApplication.getBibTeX>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('No entry was selected.'))
        else:
            try:
                self.data.currentEntryBibTeX = self.APP.getBibTeX(self.data.currentEntryId)
            except Exception, e:
                self.__sendError(e)
    
    def getDisplayedEntryCount(self):
        """
        Get the total number of entries currently displayed.
        
        An C{error} event is sent to the statechart if there is no entry list displayed.
        @rtype: L{int}
        @return: The total number of entries.
        @note: A total of 0 is not considered as an error.
        """
        if self.data.entryList is None:
            self.__sendError(ControllerLogicException('No entry list found.'))
        else:
            return len(self.data.entryList)
    
    def getAllEntries(self):
        """
        Load all entries in L{EntryDict<gui.app_interface.IApplication.EntryDict>} format.
        
        C{success} or C{fail} event is sent to the statechart if operation is successful or not.
        
        An C{error} event is sent to the statechart if no entry was loaded
        or L{IApplication.getAllEntries<gui.app_interface.IApplication.getAllEntries>} raised an exception.
        """
        try:
            self.data.entryList = self.APP.getAllEntries()
            if not self.__sendAppOperationResult(lambda: self.data.entryList is not None,
                                                 ControllerLogicException('Load entries failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    #####################
    # Actions: Interface from statechart to GUI
    #####################
    
    def isBibtexFileLoaded(self):
        """
        Verify if a BibTeX file is currently open.
        @rtype: L{bool}
        @return: C{True} a BibTeX file is open, C{False} otherwise.
        """
        return self.data.bibtexFilepath is not None
    
    def isEntrySelected(self):
        """
        Verify if an entry is currently selected in the list.
        
        An C{error} event is sent to the statechart if
        or L{MainWindow.isEntrySelected<gui.gui.MainWindow.isEntrySelected>} raised an exception.
        @rtype: L{bool}
        @return: C{True} an entry is selected, C{False} otherwise.
        """
        try:
            return self.GUI.isEntrySelected()
        except Exception, e:
            self.__sendError(e)
    
    def setDirtyTitle(self):
        """
        Show that the currently open file has been modified in the title bar of the window.
        
        An C{error} event is sent to the statechart if
        or L{MainWindow.setDirtyTitle<gui.gui.MainWindow.setDirtyTitle>} raised an exception.
        """
        try:
            result = self.GUI.setDirtyTitle()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Set dirty title failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def unsetDirtyTitle(self):
        """
        Show that the currently open file has not been changed since its last save in the title bar of the window.
        
        An C{error} event is sent to the statechart if
        or L{MainWindow.unsetDirtyTitle<gui.gui.MainWindow.unsetDirtyTitle>} raised an exception.
        """
        try:
            result = self.GUI.unsetDirtyTitle()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Unset dirty title failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def displayEntries(self):
        """
        Display the currently loaded entries in the list of entries.
        
        An C{error} event is sent to the statechart if there is no entry list displayed
        or L{MainWindow.displayEntries<gui.gui.MainWindow.displayEntries>} raised an exception.
        """
        if self.data.entryList is None:
            self.__sendError(ControllerLogicException('No entry list found.'))
        else:
            try:
                result = self.GUI.displayEntries(self.data.entryList)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Display entries failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def addNewEntryRow(self):
        """
        Add a new row for the newly created entry.
        
        An C{error} event is sent to the statechart if the current entry was not converted into an L{EntryDict<gui.app_interface.EntryDict>},
        or L{MainWindow.addNewEntryRow<gui.gui.MainWindow.addNewEntryRow>} raised an exception.
        """
        if self.data.currentEntryDict is None:
            self.__sendError(ControllerLogicException('Entry must be converted to dictionary format.'))
        else:
            try:
                result = self.GUI.addNewEntryRow(self.data.currentEntryDict)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Add new entry row failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def updateSelectedEntryRow(self):
        """
        Modify the values in the row of the selected entry.
        
        An C{error} event is sent to the statechart if the current entry was not converted into an L{EntryDict<gui.app_interface.EntryDict>},
        or L{MainWindow.updateSelectedEntryRow<gui.gui.MainWindow.updateSelectedEntryRow>} raised an exception.
        """
        if self.data.currentEntryDict is None:
            self.__sendError(ControllerLogicException('Entry must be converted to dictionary format.'))
        else:
            try:
                result = self.GUI.updateSelectedEntryRow(self.data.currentEntryDict)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Update row failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def removeEntryRow(self):
        """
        Delete the row of the selected entry.
        
        An C{error} event is sent to the statechart if there is no entry was selected
        or L{MainWindow.removeEntryRow<gui.gui.MainWindow.removeEntryRow>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('Entry not found.'))
        else:
            try:
                result = self.GUI.removeEntryRow(self.data.currentEntryId)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Remove row failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def selectCurrentEntryRow(self):
        """
        Highlight the row of the selected entry.
        
        An C{error} event is sent to the statechart if there is no entry was selected
        or L{MainWindow.selectEntryRow<gui.gui.MainWindow.selectEntryRow>} raised an exception.
        """
        if self.data.currentEntryId is None:
            self.__sendError(ControllerLogicException('Entry not found.'))
        else:
            try:
                result = self.GUI.selectEntryRow(self.data.currentEntryId)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Select row failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def unselectEntryRow(self):
        """
        Unselect the row of the selected entry.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.unselectEntryRow<gui.gui.MainWindow.unselectEntryRow>} raised an exception.
        """
        try:
            result = self.GUI.unselectEntryRow()
            if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Unselect row failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def clearList(self):
        """
        Delete all rows.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.clearList<gui.gui.MainWindow.clearList>} raised an exception.
        """
        try:
            result = self.GUI.clearList()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Clear list failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def displayBibTexInEditor(self):
        """
        Replace text in the BibTeX editor with the BibTeX format of the selected entry.
        
        An C{error} event is sent to the statechart if the entry was not converted to BibTeX format
        or L{MainWindow.displayBibTexInEditor<gui.gui.MainWindow.displayBibTexInEditor>} raised an exception.
        """
        if self.data.currentEntryBibTeX is None:
            self.__sendError(ControllerLogicException('Entry must be converted to BibTeX format.'))
        else:
            try:
                result = self.GUI.displayBibTexInEditor(self.data.currentEntryBibTeX)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Display in editor failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def clearEditor(self):
        """
        Remove all the text from the editor.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.clearEditor<gui.gui.MainWindow.clearEditor>} raised an exception.
        """
        try:
            result = self.GUI.clearEditor()
            if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Clear editor failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def previewEntryHTML(self):
        """
        Display the HTML format of the selected entry in the previewer.
        
        An C{error} event is sent to the statechart if the entry was not converted to HTML format
        or L{MainWindow.previewEntry<gui.gui.MainWindow.previewEntry>} raised an exception.
        """
        if self.data.currentEntryHTML is None:
            self.__sendError(ControllerLogicException('Entry must be converted to HTML format.'))
        else:
            try:
                result = self.GUI.previewEntry(self.data.currentEntryHTML)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Preview entry failed.')):
                    return
            except Exception, e:
                self.__sendError(e)
    
    def clearPreviewer(self):
        """
        Remove all content from the previewer.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.clearPreviewer<gui.gui.MainWindow.clearPreviewer>} raised an exception.
        """
        try:
            result = self.GUI.clearPreviewer()
            if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Clear previewer failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def openEntryPaper(self):
        """
        Open the paper of the selected entry if its I{paper} field is not empty.
        
        An C{error} event is sent to the statechart if the entry has no paper
        or L{MainWindow.openURL<gui.gui.MainWindow.openURL>} raised an exception.
        """
        try:
            self.getEntryPaperURL()
            if self.currentEntryHasPaper():
                result = self.GUI.openURL(self.data.currentEntryPaperURL)
                if not self.__sendAppOperationResult(lambda: result,
                                                     ControllerLogicException('Open paper failed.')):
                    return
        except Exception, e:
            self.__sendError(e)
    
    def popupOpenDialog(self):
        """
        Open the I{Open File} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupOpenDialog<gui.gui.MainWindow.popupOpenDialog>} raised an exception.
        """
        try:
            self.GUI.popupOpenDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupSaveDialog(self):
        """
        Open the I{Save As} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupSaveDialog<gui.gui.MainWindow.popupSaveDialog>} raised an exception.
        """
        try:
            self.GUI.popupSaveDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupImportDialog(self):
        """
        Open the I{Import File} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupImportDialog<gui.gui.MainWindow.popupImportDialog>} raised an exception.
        """
        try:
            self.GUI.popupImportDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupExportDialog(self):
        """
        Open the I{Export File} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupExportDialog<gui.gui.MainWindow.popupExportDialog>} raised an exception.
        """
        try:
            self.GUI.popupExportDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupSearchDialog(self):
        """
        Open the I{Search} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupSearchDialog<gui.gui.MainWindow.popupSearchDialog>} raised an exception.
        """
        try:
            self.GUI.popupSearchDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupPreferencesDialog(self):
        """
        Open the I{Preferences} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupPreferencesDialog<gui.gui.MainWindow.popupPreferencesDialog>} raised an exception.
        """
        try:
            self.GUI.popupPreferencesDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupAboutDialog(self):
        """
        Open the I{About} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupAboutDialog<gui.gui.MainWindow.popupAboutDialog>} raised an exception.
        """
        try:
            result = self.GUI.popupAboutDialog()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Open about dialog failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def popupUserManualWindow(self):
        """
        Open the I{User Manual} window.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupUserManualWindow<gui.gui.MainWindow.popupUserManualWindow>} raised an exception.
        """
        try:
            result = self.GUI.popupUserManualWindow()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Open user manual failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def popupConfirmExitDialog(self):
        """
        Open the I{Confirm Exit} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupConfirmExitDialog<gui.gui.MainWindow.popupConfirmExitDialog>} raised an exception.
        """
        try:
            self.GUI.popupConfirmExitDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupPendingChangesOnExitDialog(self):
        """
        Open the I{Pending Changes} dialog.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupPendingChangesOnExitDialog<gui.gui.MainWindow.popupPendingChangesOnExitDialog>} raised an exception.
        """
        try:
            self.GUI.popupPendingChangesOnExitDialog()
        except Exception, e:
            self.__sendError(e)
    
    def popupErrorMessage(self, msg=None):
        """
        Open a dialog showing an error message.
        @type msg: L{str}
        @param msg: The message to display.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.popupErrorMessage<gui.gui.MainWindow.popupErrorMessage>} raised an exception.
        """
        if msg is None:
            msg = self.data.errorMsg
        try:
            self.GUI.popupErrorMessage(msg)
        except Exception, e:
            self.__sendError(e)
    
    def setStatusMsg(self, msg):
        """
        Set the status bar message
        @type msg: L{str}
        @param msg: The message to display.
        
            >>> setStatusMsg('hello')
            >>> updateStatusBar()    # will display hello
        """
        self.data.statusMsg = msg
    
    def updateStatusBar(self, msg=None):
        """
        Display a message in the status bar.
        @type msg: L{str}
        @param msg: The message to display.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.updateStatusBar<gui.gui.MainWindow.updateStatusBar>} raised an exception.
        """
        if msg is None:
            msg = self.data.statusMsg
        try:
            self.GUI.updateStatusBar(msg)
        except Exception, e:
            self.__sendError(e)
    
    def clearStatusBar(self):
        """
        Clear any message in the status bar.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.clearStatusBar<gui.gui.MainWindow.clearStatusBar>} raised an exception.
        """
        try:
            self.GUI.clearStatusBar()
        except Exception, e:
            self.__sendError(e)
    
    def updateStatusTotal(self):
        """
        Display the total number of entries currently displayed in the right status bar.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.updateStatusBarTotal<gui.gui.MainWindow.updateStatusBarTotal>} raised an exception.
        """
        try:
            result = self.GUI.updateStatusBarTotal(self.getDisplayedEntryCount())
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Update toal in status bar failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def enableClearFilter(self):
        """
        Enable the I{Clear Filer} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.enableClearFilter<gui.gui.MainWindow.enableClearFilter>} raised an exception.
        """
        try:
            result = self.GUI.enableClearFilter()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Enable clear filter failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def disableClearFilter(self):
        """
        Disable the I{Clear Filer} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.disableClearFilter<gui.gui.MainWindow.disableClearFilter>} raised an exception.
        """
        try:
            result = self.GUI.disableClearFilter()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Disable clear filter failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def enableDelete(self):
        """
        Enable the I{Delete} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.enableDelete<gui.gui.MainWindow.enableDelete>} raised an exception.
        """
        try:
            result = self.GUI.enableDelete()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Enable delete failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def disableDelete(self):
        """
        Disable the I{Delete} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.disableDelete<gui.gui.MainWindow.disableDelete>} raised an exception.
        """
        try:
            result = self.GUI.disableDelete()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Disable delete failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def enableDuplicate(self):
        """
        Enable the I{Duplicate} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.enableDuplicate<gui.gui.MainWindow.enableDuplicate>} raised an exception.
        """
        try:
            result = self.GUI.enableDuplicate()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Enable duplicate failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def disableDuplicate(self):
        """
        Disable the I{Duplicate} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.disableDuplicate<gui.gui.MainWindow.disableDuplicate>} raised an exception.
        """
        try:
            result = self.GUI.disableDuplicate()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Disable duplicate failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def enableUndo(self):
        """
        Enable the I{Undo} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.enableUndo<gui.gui.MainWindow.enableUndo>} raised an exception.
        """
        try:
            result = self.GUI.enableUndo()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Enable undo failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def disableUndo(self):
        """
        Disable the I{Undo} menu.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.disableUndo<gui.gui.MainWindow.disableUndo>} raised an exception.
        """
        try:
            result = self.GUI.disableUndo()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Disable undo failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def enableUpdateButton(self):
        """
        Enable the I{Update} button.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.enableUpdateButton<gui.gui.MainWindow.enableUpdateButton>} raised an exception.
        """
        try:
            result = self.GUI.enableUpdateButton()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Enable update failed.')):
                return
        except Exception, e:
            self.__sendError(e)
    
    def disableUpdateButton(self):
        """
        Disable the I{Update} button.
        
        An C{error} event is sent to the statechart if
        L{MainWindow.disableUpdateButton<gui.gui.MainWindow.disableUpdateButton>} raised an exception.
        """
        try:
            result = self.GUI.disableUpdateButton()
            if not self.__sendAppOperationResult(lambda: result,
                                                 ControllerLogicException('Disable undo failed.')):
                return
        except Exception, e:
            self.__sendError(e)
