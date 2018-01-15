'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This module represents the interface that the L{app} module must conform to.
@group Interchange data-structures: EntryDict, EntryListColumn
@sort: EntryDict, EntryListColumn
'''

class EntryListColumn(object):
    """
    The columns of the entry list.
    """
    AUTHOR = 'author'
    ID = 'id'
    KEY = 'entrykey'
    PAPER = 'paper'
    TITLE = 'title'
    TYPE = 'entrytype'
    YEAR = 'year'
    @staticmethod
    def list():
        """
        @rtype: L{list}
        @return: A list of all the columns.
        """
        return [EntryListColumn.AUTHOR, EntryListColumn.ID, EntryListColumn.KEY, EntryListColumn.PAPER,
                EntryListColumn.TITLE, EntryListColumn.TYPE, EntryListColumn.YEAR]

class EntryDict(dict):
    """
    The exchange format of entries.
    It is a dictionary where all L{EntryListColumn} fields are predefined keys that cannot be removed.
    
        >>> d = EntryDict()
        >>> print d
            {'id': '', ...}
        >>> del d[EntryListColumn.ID]
        >>> print d
            {'id': '', ...}
    """
    def __init__(self, *args):
        """
        All L{EntryListColumn} fields are predefined keys.
        """
        dict.__init__(self, args)
        for key in EntryListColumn.list():
            if key not in self.iterkeys():
                if key == EntryListColumn.ID:
                    self[key] = 0
                else:
                    self[key] = ''
        
    def __delitem__(self, key):
        """
        Deleting a L{EntryListColumn} key will set its value to C{''}.
        """
        if key not in EntryListColumn.list():
            dict.__delitem__(key)
        elif key == EntryListColumn.ID:
            raise KeyError('Cannot delete key: ' + EntryListColumn.ID)
        else:
            self[key] = ''
    
    def toBibTeX(self):
        #@TYPE{KEY,
        #  FIELD1 = {VALUE1},
        #  FIELD2 = {VALUE2}
        #}
        forbiddenFields = [EntryListColumn.TYPE, EntryListColumn.KEY, EntryListColumn.ID]
        try:
            bibtex = '@%s{%s' % (self[EntryListColumn.TYPE], self[EntryListColumn.KEY])
            for col in self.iterkeys():
                if col in forbiddenFields:
                    continue
                bibtex += ',\n  %s = {%s}' % (col, self[col])
            bibtex += '\n}'
            return bibtex
        except:
            return ''
    
    @staticmethod
    def fromDict(d):
        """
        Convert a Python L{dict} into an L{EntryDict}.
        @type d: L{dict}
        @param d: The dictionary to convert.
        @rtype: L{EntryDict}
        @return: An L{EntryDict} with all the keys and values from C{d}.
        """
        ed = EntryDict()
        for k in d:
            ed[k] = d[k]
        return ed

class IApplication(object):
    """
    Interface that provides all the application functions required for the L{Controller<gui.controller.Controller>}.
    The meaning of every operation in the BiBler GUI is given by these functions.
    """
    
    def start(self):
        """
        Start the application.
        """
        raise NotImplementedError()
    
    def exit(self):
        """
        Close the application.
        """
        raise NotImplementedError()
    
    def importFile(self, path, importFormat):
        """
        Import a list of entries from a file in a given format.
        @type path: L{str}
        @param path: The path to a file.
        @type importFormat: L{utils.settings.ImportFormat}
        @param importFormat: The format of the file.
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def exportFile(self, path, exportFormat):
        """
        Export the list of entries to a file in a given format.
        @type path: L{str}
        @param path: The path to a file.
        @type exportFormat: L{utils.settings.ExportFormat}
        @param exportFormat: The format of the file.
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def openFile(self, path):
        """
        Import a list of entries from a BibTeX file in a given format and overwrites all existing entries.
        @type path: L{str}
        @param path: The path to a file.
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def addEntry(self, entryBibTeX=None):
        """
        Add a new entry. If C{entryBibTeX==None}, an empty entry is created.
        @type entryBibTeX: L{str}
        @param entryBibTeX: The BibTeX reference of the entry. 
        @rtype: L{int}
        @return: The I{id} of the new entry. C{None} is returned if failed.
        """
        raise NotImplementedError()
    
    def duplicateEntry(self, entryId):
        """
        Create a copy of an existing entry.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry to copy.
        @rtype: L{int}
        @return: The I{id} of the new entry. C{None} is returned if failed.
        """
        raise NotImplementedError()
    
    def updateEntry(self, entryId, entryBibTeX):
        """
        Update an entry with a new BibTeX reference.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry to update. 
        @type entryBibTeX: L{str}
        @param entryBibTeX: The BibTeX reference. 
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()
    
    def deleteEntry(self, entryId):
        """
        Delete an entry.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry to delete. 
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
    
    def previewEntry(self, entryId):
        """
        Convert an entry into its HTML representation following the bibliography style specified in L{utils.settings.Preferences}.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry to preview. 
        @rtype: L{str}
        @return: The HTML representation of the entry.
        @raise L{Exception}: If entry not found.
        """
        raise NotImplementedError()
    
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
        """
        Get the URL of the paper of the selected entry.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry. 
        @rtype: L{str}
        @return: The URL (or path) to the file.
        @raise L{Exception}: If entry not found.
        """
        raise NotImplementedError()
    
    def search(self, query):
        """
        Search for entries that satisfy the query provided.
        @type query: L{str}
        @param query: The query to match.
        @rtype: L{int}
        @return: Number of matches if search succeeded, negative number otherwise.
        """
        raise NotImplementedError()
    
    def sort(self, field):
        """
        Inplace sort of in alphabetically increasing order all entries with respect to a field.
        @type field: L{EntryListColumn}
        @param field: The field to sort on.
        @rtype: L{bool}
        @return: C{True} if succeeded, C{False} otherwise.
        """
        raise NotImplementedError()

    def getEntry(self, entryId):
        """
        Convert an entry into an L{EntryDict}.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry. 
        @rtype: L{list} of L{EntryDict}
        @return: The entry.
        @raise L{Exception}: If entry not found.
        """
        raise NotImplementedError()

    def getBibTeX(self, entryId):
        """
        Convert an entry into its BibTeX reference.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry. 
        @rtype: L{str}
        @return: The BibTeX reference.
        @raise L{Exception}: If entry not found.
        """
        raise NotImplementedError()
    
    def getAllEntries(self):
        """
        Get the list of all entries.
        @rtype: L{list} of L{EntryDict}
        @return: The list of entries.
        """
        raise NotImplementedError()
    
    def getEntryCount(self):
        """
        Get the total number of entries.
        @rtype: L{int}
        @return: The total.
        """
        raise NotImplementedError()
    
    def getSearchResult(self):
        """
        Get the list of entries filtered by the search.
        @rtype: L{list} of L{EntryDict}
        @return: The list of entries.
        """
        raise NotImplementedError()
        
    def iterAllEntries(self):
        """
        Iterator over the list of all entries.
        @rtype: L{generator object} of L{EntryDict}
        @return: The list of entries.
        """
        raise NotImplementedError()
        
    def iterSearchResult(self):
        """
        Get the list of entries filtered by the search.
        @rtype: L{generator object} of L{EntryDict}
        @return: The list of entries.
        """
        raise NotImplementedError()
