from gui.app_interface import IApplication
from reference_manager import ReferenceManager
from impex import Importer
from impex import Exporter
from field_name import FieldName
from entry import Entry
from entry import EmptyEntry
from utils import settings



from reference_manager import ReferenceManager
refmanager = ReferenceManager()

class Command(object):
     
    def execute(self, entryBibTeX):
        raise NotImplementedError()
    
    
class Invoker:
    
    def invoke(self, command, entryBibTeX):
        command.execute(entryBibTeX)

    
class AddEntry(Command):
#     refmanager = ReferenceManager()
    
    def __init__(self, refman):
        
        self.refmanager = refman
        
                         
    #Override    
    def execute(self, entryBibTeX):
        
        self.refmanager.add(entryBibTeX)


class DeleteEntry(Command):
#     refmanager = ReferenceManager()
    
    def __init__(self, refman):
        self.refmanager = refman
        
    #Override    
    def execute(self, entryBibTeX):
        self.refmanager.delete(entryId)

class Update(Command):
    
    def __init__(self, entryid, entryBibTeX):
        self.refmanager = entryid
        sel.entryBibTeX = entryBibTeX
    
    #Override    
    def execute(self, entryid, entryBibTeX):
        self.refmanager.update(entryId, entryBibTeX)

class Duplicate(Command):
#     refmanager = ReferenceManager()
    
    def __init__(self, refman):
        self.refmanager = refman
        
    #Override    
    def execute(self, entryid):
        self.refmanager.duplicate(entryId)

class Search(Command):
    
    def __init__(self, refman):
        self.refmanager = refman
    #Override    
    def execute(self, query):
        self.refmanager.search(query)
        
class Sort(Command):
    
    def __init__(self, refman):
        self.refmanager = refman
    #Override    
    def execute(self, field):
        self.refmanager.search(field)

class ImportFile(Command):
    
    def __init__(self, path, importFormat):
        self.refmanager = path
        sel.importFormat = importFormat
    
    #Override    
    def execute(self, path, importFormat):
        self.refmanager.importFile(path, importFormat)


class ExportFile(Command):
    
    def __init__(self, path, exportFormat):
        self.refmanager = path
        sel.exportFormat = exportFormat
    
    #Override    
    def execute(self, path, exportFormat):
        self.refmanager.exportFile(path, exportFormat)

class OpenFile(Command):
    
    def __init__(self, refman):
        self.refmanager = refman
    #Override    
    def execute(self, path):
        self.refmanager.openFile(path)

class PreviewEntry(Command):
#     refmanager = ReferenceManager()
    
    def __init__(self, refman):
        self.refmanager = refman
        
    #Override    
    def execute(self, entryid):
        self.refmanager.previewEntry(entryId)


class Undo(Command):
#     refmanager = ReferenceManager()
    
    def __init__(self):
        pass
            
    #Override    
    def execute(self):
        self.refmanager.undo()
