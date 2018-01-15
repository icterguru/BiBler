from gui.app_interface import IApplication
from reference_manager import ReferenceManager
from impex import Importer
from impex import Exporter
from field_name import FieldName
from entry import Entry
from entry import EmptyEntry
from utils import settings



from reference_manager import ReferenceManager

class Command(object):
     
    def execute(self, entryBibTeX):
        raise NotImplementedError()
    
    
class AddEntry(Command):
    refmanager = ReferenceManager()
    
    def __init__(self, refman):
        
        self.refmanager = refman
        
                         
    #Override    
    def execute(self, entryBibTeX):
        
        self.refmanager.add(entryBibTeX)


class DeleteEntry(Command):
    refmanager = ReferenceManager()
    
    def __init__(self, id):
        self.refmanager = id
        
    #Override    
    def execute(self, entryBibTeX):
        self.refmanager.delete(entryId)

    
class Invoker:
    
    def invoke(self, command, entryBibTeX):
        command.execute(entryBibTeX)



# update(entryId, entryBibTeX)
# deleteAll()
# duplicate(entryId)
# search(query)
# sort(field)
# exporter= Exporter() 
# bibtexExport()
# csvExport()
# htmlIEEETransExport()
# htmlACMExport()
# importer = Importer()
# bibtexImport()
# csvImport()
# importFile(path, importFormat)
# exportFile(path, exportFormat)
# openFile(path)
# previewEntry(entryId)
# undo()
# hasUndoableActionLeft()
# getEntryPaperURL(entryId)
# search(query)
# sort(field)
# getEntry(entryId)
# getBibTeX(entryId)
# getAllEntries()
# getEntryCount()
# getSearchResult()
# iterAllEntries()
# iterSearchResult()
