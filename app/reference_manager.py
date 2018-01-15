

from entry import EmptyEntry
from bibtex_parser import BibTeXParser
from field_name import FieldName
from gui.app_interface import EntryListColumn

class ReferenceManager(object):
    def __init__(self):
        self.searchResult = list()
        self.entryList = list()
        pass
        
        
    def add(self, entryBibTeX):
        if entryBibTeX == None:
            entry = EmptyEntry()
            entry.generateId()
            self.entryList.append(entry)
            return entry.getId()
        try:
            parser = BibTeXParser(entryBibTeX)
            entry = parser.parse()
            self.__setKey(entry)
            if entry.validate():
                entry.generateId()
                self.entryList.append(entry)
                return entry.getId()
            else:
                return None
        except:
            return None
        
    #def add(self, entryBibTeX):
    
    
    def update(self, entryId, entryBibTeX):
        entry = self.getEntry(entryId)
        if entry == None:
            return False
        try:
            parser = BibTeXParser(entryBibTeX)
            new_entry = parser.parse()
            new_entry.setId(entryId)
            self.__setKey(new_entry)
            if new_entry.validate():
                # Overwrite the entry in entryList
                self.entryList[self.entryList.index(entry)] = new_entry
            else:
                return False
        except Exception, e:
            raise e
        return True
        
    def delete(self, entryId):
        entry = self.getEntry(entryId)
        if entry == None:
            return False
        self.entryList.remove(entry)
        return True
        
    def deleteAll(self):
        self.entryList = []
        self.searchResult = []
        
    def duplicate(self, entryId):
        entry = self.getEntry(entryId)
        if entry == None:
            return None
        return self.add(entry.toBibTeX())
        
    def search(self, query):
        try:
            self.searchResult = filter(lambda e: e.matches(query), self.entryList)
            return len(self.searchResult)
        except:
            return -1
    
    def sort(self, field):
        def getField(e, field):
            try:
                return e.getFieldValue(FieldName.fromEntryListColumn(field))
            except:
                return ''
        try:
            if field == EntryListColumn.TYPE:
                self.entryList.sort(key=lambda e: e.getEntryType())
            elif field == EntryListColumn.ID:
                self.entryList.sort(key=lambda e: e.getId())
            else:
                self.entryList.sort(key=lambda e: getField(e, field))
            return True
        except:
            return False
    
    def undo(self):
        pass;
     
    def getEntry(self, entryId):
        for e in self.entryList:
            if e.getId() == entryId:
                return e
        return None
        
    def iterEntryList(self):
        for entry in self.entryList:
            yield entry
        
    def getEntryCount(self):
        return len(self.entryList)
        
    def iterSearchResult(self):
        for entry in self.searchResult:
            yield entry
        
    def __setKey(self, entry):
        key = entry.generateKey()
        duplicateKeys = map(lambda e: e.getKey(),    # collect all keys that start with the same key
                            filter(lambda e: e.getId() != entry.getId() and e.getKey().startswith(key), self.entryList))
        if len(duplicateKeys) > 27:
            raise Exception('Too many entries with the same key.')
        elif not duplicateKeys:
            entry.setKey(key)
        else:
            suffix = ''
            for i in xrange(len(duplicateKeys) + 1):
                if key + suffix not in duplicateKeys:
                    entry.setKey(key + suffix)
                    break
                suffix = chr(ord('a') + i)
