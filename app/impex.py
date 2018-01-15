
from field_name import FieldName


class ImpEx(object):
    def __init__(self, path):
        self.path = path
        self.database = None
    
    def openDB(self, mode):
        try:
            self.database = open(self.path, mode)
        except:
            raise Exception('Cannot open the requested file.')
    
    def closeDB(self):
        self.database.close()



class Exporter(ImpEx):
    def __init__(self, path, entries):
        super(Exporter, self).__init__(path)
        self.entries = entries
        
    def bibtexExport(self):
        self.openDB('w')
        return self.__export(lambda e: e.toBibTeX())
        
    def csvExport(self):
        self.openDB('w')
        self.database.write('entrytype\t' + '\t'.join(FieldName.getAllFieldNames()) + '\n')    # headers
        return self.__export(lambda e: e.toCSV())
        
    def htmlIEEETransExport(self):
        self.openDB('w')
        return self.__export(lambda e: e.toHtmlIEEETrans())
        
    def htmlACMExport(self):
        self.openDB('w')
        return self.__export(lambda e: e.toHtmlACM())
    
    def __export(self, exporter):
        total = 0
        try:
            for entry in self.entries:
                bibtex = exporter(entry)
                self.database.write(bibtex + '\n')
                total += 1
        except:
            raise
        finally:
            self.closeDB()
        return total


class Importer(ImpEx):
    def __init__(self, path, manager):
        super(Importer, self).__init__(path)
        self.manager = manager
        
        
    def bibtexImport(self):
        self.openDB('r')
        total = 0
        try:
            line = self.database.readline()
            entry = ''
            while line:
                if line.startswith('@'):
                    if entry:
                        result = self.manager.add(entry)
                        if result > 0:
                            total += 1
                    entry = line
                else:
                    entry += line
                line = self.database.readline()
            if entry:
                result = self.manager.add(entry)
                if result > 0:
                    total += 1
        except:
            raise
        finally:
            self.closeDB()
        return total
        
    def csvImport(self):
        self.openDB('r')
        total = 0
        allFields = FieldName.getAllFieldNames()
        
        try:
            line = self.database.readline() # skip header line
            line = self.database.readline()
            while line:
                line = line.split('\t')
                if len(line) != len(allFields) + 1:
                    raise Exception('CSV file on line %d has incorrect fields.' % total)
                entry = {'entrytype': line[0]}
                for i in range(len(allFields)):
                    value = line[i + 1]
                    if value.startswith('"'):
                        value = value[1:]
                    if value.endswith('"'):
                        value = value[:-1]
                    entry[allFields[i]] = value
                bibtex = None
                # Convert to BibTeX
                bibtex = '@%s{' % entry['entrytype'] # key will be auto generated
                for field in entry.iterkeys():
                    bibtex += ',\n  %s = {%s}' % (field, entry[field])
                bibtex += '\n}'
                result = self.manager.add(bibtex)
                if result > 0:
                    total += 1            
                line = self.database.readline()
        except:
            raise
        finally:
            self.closeDB()
        return total
        
    
