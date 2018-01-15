'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This module represents the interface to the L{gui} package.
'''

from gui.app_interface import IApplication
from reference_manager import ReferenceManager
from impex import Importer
from impex import Exporter
from field_name import FieldName
from entry import Entry
from utils import settings


from undo import Invoker
from undo import AddEntry
from undo import DeleteEntry
from undo import Update
from undo import Duplicate
from undo import Search
from undo import Sort
from undo import ImportFile
from undo import ExportFile
from undo import OpenFile
from undo import PreviewEntry
from undo import Undo
 


prefs = settings.Preferences()

class UserInterface(IApplication):
    def __init__(self):
        super(UserInterface, self).__init__()
      
        self.referenceManager = ReferenceManager()
        
        self.invoker = Invoker()   # New style in CommandPattern 
        #self.addentry = AddEntry(self.referenceManager)
#         
        
    def start(self):
        pass
        
    def exit(self):
        pass
    
        
    def importFile(self, path, importFormat):
        total = 0
        importer = Importer(path, self.referenceManager)
        if importFormat == settings.ImportFormat.BIBTEX:
            total = importer.bibtexImport()
        elif importFormat == settings.ImportFormat.CSV:
            total = importer.csvImport()
        return total > 0
        
    def exportFile(self, path, exportFormat):
        total = 0
        exporter = Exporter(path, self.referenceManager.iterEntryList())
        if exportFormat == settings.ExportFormat.BIBTEX:
            total = exporter.bibtexExport()
        elif exportFormat == settings.ExportFormat.CSV:
            total = exporter.csvExport()
        elif exportFormat == settings.ExportFormat.HTML:
            if prefs.bibStyle == settings.BibStyle.ACM:
                total = exporter.htmlACMExport()
            elif prefs.bibStyle == settings.BibStyle.IEEE:
                total = exporter.htmlIEEETransExport()
        return total > 0
        
    def openFile(self, path):
        self.referenceManager.deleteAll()
        Entry.resetId()
        return self.importFile(path, settings.ImportFormat.BIBTEX)
        
    def addEntry(self, entryBibTeX):
        
         #return self.referenceManager.add(entryBibTeX)  # Old codes
         
         # The following two lines are new codes in terms of Command Pattern
               
         self.addentry = AddEntry(self.referenceManager)
         return self.invoker.invoke(self.addentry, entryBibTeX)

               
    def duplicate(self, entryId):
        #return self.referenceManager.duplicate(entryId)
        self.duplicate = Duplicate(self.referenceManager)
        return self.invoker.invoke(self.duplicate, entryId)

        
    def updateEntry(self, entryId, entryBibTeX):
#         return self.referenceManager.update(entryId, entryBibTeX)

        self.updateentry = UpdateEntry(self.referenceManager, entryId, entryBibTeX)
        return self.invoker.invoke(self.updateentry, entryId, entryBibTeX)

        
    def deleteEntry(self, entryId):
#         return self.referenceManager.delete(entryId)
         self.deleteentry = DeleteEntry(self.referenceManager)
         return self.invoker.invoke(self.deleteentry, entryId)

        
    def previewEntry(self, entryId):
        entry = self.referenceManager.getEntry(entryId)
        if entry:
            if prefs.bibStyle == settings.BibStyle.ACM:
                return entry.toHtmlACM()
            elif prefs.bibStyle == settings.BibStyle.IEEE:
                return entry.toHtmlIEEETrans()
        raise Exception('entry not found.')
        
    def undo(self):
        """
        Undo the last action performed. 
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def hasUndoableActionLeft(self):
        """
        Verify if there is any action to undo.
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def getEntryPaperURL(self, entryId):
        entry = self.referenceManager.getEntry(entryId)
        if entry:
            return entry.getFieldValue(FieldName.Paper)
        raise Exception('entry not found.')
        
    def search(self, query):
        return self.referenceManager.search(query)
        
    def sort(self, field):
        return self.referenceManager.sort(field) 
        
    def getEntry(self, entryId):
        entry = self.referenceManager.getEntry(entryId)
        if entry:
            return entry.toEntryDict()
        raise Exception('entry not found.')
        
    def getBibTeX(self, entryId):
        entry = self.referenceManager.getEntry(entryId)
        if entry:
            return entry.toBibTeX()
        raise Exception('entry not found.')
        
    def getAllEntries(self):
        entries = []
        for entry in self.referenceManager.iterEntryList():
            entries.append(entry.toEntryDict())
        return entries
        
    def getEntryCount(self):
        return self.referenceManager.getEntryCount()
        
    def getSearchResult(self):
        entries = []
        for entry in self.referenceManager.iterSearchResult():
            entries.append(entry.toEntryDict())
        return entries
        
    def iterAllEntries(self):
        yield self.referenceManager.iterEntryList().toEntryDict()
        
    def iterSearchResult(self):
        yield self.referenceManager.iterSearchResult().toEntryDict()
        
    
