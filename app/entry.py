
from gui.app_interface import EntryDict, EntryListColumn
from field_name import FieldName
from field import Author, Editor, Field, Organization, Pages, Year

class Entry(object):
    __lastID = 0
    def __init__(self):
        self._id = None
        self.entryType = ''
        self.key = ''
        self.requiredFields = dict()
        self.optionalFields = {FieldName.Key: Field(FieldName.Key)}
        self.additionalFields = {FieldName.Annote: Field(FieldName.Annote),
                                 FieldName.Paper: Field(FieldName.Paper),
                                 FieldName.Comment: Field(FieldName.Comment)}
        
    def getId(self):
        return self._id
    
    def setId(self, _id):
        self._id = _id
    
    def generateId(self):
        Entry.__lastID += 1
        self._id = Entry.__lastID
    
    def getEntryType(self):
        return self.entryType
        
    def getKey(self):
        return self.key
    
    def setKey(self, key):
        self.key = key
    
    def generateKey(self):
        key = self.getField(FieldName.Key)
        if not key.isEmpty():
            key = Field.simplify(key.getValue())
        else:
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Author).getFirstLastName())
        return key + self.getField(FieldName.Year).getYear()
        
    def getField(self, field):
        if field in self.requiredFields:
            return self.requiredFields[field]
        elif field in self.optionalFields:
            return self.optionalFields[field]
        elif field in self.additionalFields:
            return self.additionalFields[field]
        else:
            raise Exception('Invalid field requested.')
        
    def getFieldValue(self, field):
        return self.getField(field).getValue()
        
    def setField(self, field, value):
        if field in self.requiredFields:
            self.requiredFields[field].setValue(value)
        elif field in self.optionalFields:
            self.optionalFields[field].setValue(value)
        elif field in self.additionalFields:
            self.additionalFields[field].setValue(value)
    
    def formatField(self, field):
        self.getField(field).format()
        
    def getAllFields(self):
        # Sorted deterministic list of fields: first required then optional then additional
        for field in self.iterRequiredFields():
            yield field
        for field in self.iterOptionalFields():
            yield field
        for field in self.iterAdditionalFields():
            yield field
        
    def iterRequiredFields(self):
        # Sorted deterministic list
        for field in sorted(self.requiredFields.iterkeys()):
            yield field
        
    def iterOptionalFields(self):
        # Sorted deterministic list
        for field in sorted(self.optionalFields.iterkeys()):
            yield field
        
    def iterAdditionalFields(self):
        # Sorted deterministic list
        for field in sorted(self.additionalFields.iterkeys()):
            yield field
        
    def validate(self):
        # Check that all required fields are not empty
        for field in self.requiredFields:
            if self.requiredFields[field].isEmpty():
                return False
        return True
        
    def matches(self, query):
        query = query.lower()
        for field in self.requiredFields.iterkeys():
            if field == FieldName.Paper:
                continue
            if query in Field.simplify(self.requiredFields[field].getValue()).lower():
                return True
        for field in self.optionalFields.iterkeys():
            if field == FieldName.Paper:
                continue
            if query in Field.simplify(self.optionalFields[field].getValue()).lower():
                return True
        for field in self.additionalFields.iterkeys():
            if field == FieldName.Paper:
                continue
            if query in Field.simplify(self.additionalFields[field].getValue()).lower():
                return True
        return False
    
    def __str__(self):
        return self.toBibTeX()
    
    def toEntryDict(self):
        e = EntryDict()
        e[EntryListColumn.ID] = self.getId()
        e[EntryListColumn.TYPE] = self.getEntryType()
        e[EntryListColumn.KEY] = self.getKey()
        for field in self.iterRequiredFields():
            col = FieldName.toEntryListColumn(field)
            e[col] = self.requiredFields[field].getValue()
        for field in self.iterOptionalFields():
            col = FieldName.toEntryListColumn(field)
            e[col] = self.optionalFields[field].getValue()
        for field in self.iterAdditionalFields():
            col = FieldName.toEntryListColumn(field)
            e[col] = self.additionalFields[field].getValue()
        return e
        
    def toBibTeX(self):
        #@TYPE{KEY,
        #  FIELD1 = {VALUE1},
        #  FIELD2 = {VALUE2}
        #}
        try:
            bibtex = '@%s{%s' % (self.getEntryType(), self.getKey())
            for field in self.getAllFields():
                value = self.getFieldValue(field)
                # This part is to put {} around capital letters if they aren't already
                v = ''
                for i in xrange(len(value)):
                    if value[i].isupper():
                        if 0 < i < len(value) - 1 and value[i-1] != '{' and value[i+1] != '}':
                            v += '{%s}' % value[i]
                    else:
                        v += value[i]
                bibtex += ',\n  %s = {%s}' % (field, value)
            bibtex += '\n}'
            return bibtex
        except:
            return ''
        
    def toCSV(self):
        #"VALUE1"\t"VALUE2"
        # Where the order is determined by FieldName.getAllFieldNames()
        try:
            csv = self.getEntryType()   # the first column is the entrytype
            for field in FieldName.getAllFieldNames():
                csv += '\t'
                try:
                    csv += '"' + self.getFieldValue(field) + '"'
                except:
                    continue    # the field is not in this entrytype
            return csv
        except:
            return ''
    
    def getHtmlHeader(self):
        return '''<p><font face="verdana"><b><i>%s</i>(%s)</b></font></p>
''' % (self.getEntryType(), self.getKey())
        
    def toHtmlIEEETrans(self):
        raise NotImplementedError()
        
    def toHtmlACM(self):
        raise NotImplementedError()
    
    @staticmethod
    def getACMContributors(contributorField):
        try:
            people = []
            for contributor in contributorField.getContributors():
                person = ''
                if contributor.preposition:
                    person += contributor.preposition + ' '
                if contributor.last_name:
                    person += contributor.last_name
                if contributor.first_name:
                    person += ', ' + Field.toHTML(contributor.first_name)[0] + '.'
                people.append(person)
            if len(people) > 1:
                return ', '.join(people[:-1]) + ' and ' + people[-1]
            elif len(people) == 1:
                return people[0]
            else:
                return ''
        except:
            raise Exception('Invalid %s names.' % contributorField.getName())
    
    @staticmethod
    def resetId():
        Entry.__lastID = 0


class EmptyEntry(Entry):
        
    def __init__(self):
        super(EmptyEntry, self).__init__()
        self.entryType = ''
        self.requiredFields = dict()
        self.optionalFields = dict()
        self.additionalFields = {FieldName.Paper: Field(FieldName.Paper),
                                 FieldName.Comment: Field(FieldName.Comment)}
    
    def generateKey(self):
        return ''
    
    def validate(self):
        # No field should exist
        return not self.requiredFields.keys() and not self.optionalFields.keys()
        
    def toBibTeX(self):
        return ''
        
    def toHtmlIEEETrans(self):
        return ''
        
    def toHtmlACM(self):
        return ''
        
    
class Article(Entry):

    """
    An article from a journal or magazine.
    """
    def __init__(self):
        super(Article, self).__init__()
        self.entryType = 'ARTICLE'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.Journal: Field(FieldName.Journal),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Pages: Pages(FieldName.Pages),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    def toHtmlACM(self):
        # Capital letters are already between {}
        try:
            authors = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Author)))
            title = Field.toHTML(self.getFieldValue(FieldName.Title))
            journal = Field.toHTML(self.getFieldValue(FieldName.Journal))
            year = Field.toHTML(self.getFieldValue(FieldName.Year))
            volume = Field.toHTML(self.getFieldValue(FieldName.Volume))
            number = Field.toHTML(self.getFieldValue(FieldName.Number))
            pages = Field.toHTML(self.getFieldValue(FieldName.Pages))
            month = Field.toHTML(self.getFieldValue(FieldName.Month))
            
            html = self.getHtmlHeader()
            html += '''<p><span style="font-variant:small-caps">{0}</span> {1} <i>{2}</i>'''
            html = html.format(authors, title, journal)
            if volume:
                html += ''' <i>%s</i>''' % volume
            elif number:
                html += ''', %s''' % number
            html += ''' ('''
            if month:
                html += '''%s ''' % month
            html += '''%s)''' % year
            if pages:
                html += ''', %s''' % pages
            html += '.</p>'
            
            return html
        except:
            raise Exception('Failed to generate ACM style.')
        
    
class Book(Entry):
    """
    A book with an explicit publisher.
    """
    def __init__(self):
        super(Book, self).__init__()
        self.entryType = 'BOOK'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Editor: Editor(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.Publisher: Field(FieldName.Publisher),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Series: Field(FieldName.Series),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Edition: Field(FieldName.Edition),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
    
    def generateKey(self):
        key = self.getField(FieldName.Key)
        if not key.isEmpty():
            key = Field.simplify(key.getValue())
        elif not self.getField(FieldName.Author).isEmpty():
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Author).getFirstLastName())
        elif not self.getField(FieldName.Editor).isEmpty():
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Editor).getFirstLastName())
        return key + self.getField(FieldName.Year).getYear()
        
    def validate(self):
        author_editor_check = (self.requiredFields[FieldName.Author].isEmpty() or self.requiredFields[FieldName.Editor].isEmpty())
        return not (self.requiredFields[FieldName.Title].isEmpty() and self.requiredFields[FieldName.Publisher].isEmpty() \
                    and self.requiredFields[FieldName.Year].isEmpty() and author_editor_check)
        
    def toHtmlACM(self):
        # Capital letters are already between {}
        try:
            authors = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Author)))
            editor = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Editor)))
            title = Field.toHTML(self.getFieldValue(FieldName.Title))
            publisher = Field.toHTML(self.getFieldValue(FieldName.Publisher))
            year = Field.toHTML(self.getFieldValue(FieldName.Year))
            volume = Field.toHTML(self.getFieldValue(FieldName.Volume))
            number = Field.toHTML(self.getFieldValue(FieldName.Number))
            series = Field.toHTML(self.getFieldValue(FieldName.Series))
            address = Field.toHTML(self.getFieldValue(FieldName.Address))
            edition = Field.toHTML(self.getFieldValue(FieldName.Edition))
            month = Field.toHTML(self.getFieldValue(FieldName.Month))
            
            html = self.getHtmlHeader()
            if authors:
                html += '''<p><span style="font-variant:small-caps">%s</span>''' % authors
            else:
                html += '''<p><span style="font-variant:small-caps">%s</span>''' % editor
            html += ''' <i>%s</i>''' % title
            if edition:
                html += ''', %s ed.''' % edition
            if volume:
                html += ''', vol. %s''' % volume
            elif number:
                html += ''', %s''' % number
            if series:
                html += ''' of <i>%s</i>''' % series
            html += '''. %s,''' % publisher
            if address:
                html += ''' %s,''' % address
            if month:
                html += ''' %s''' % month
            html += ''' %s''' % year
            html += '.</p>'
            
            return html
        except:
            raise Exception('Failed to generate ACM style.')
        
    
class Booklet(Entry):
    """
    A work that is printed and bound, but without a named publisher or sponsoring institution.
    """
    def __init__(self):
        super(Booklet, self).__init__()
        self.entryType = 'BOOKLET'
        self.requiredFields = { FieldName.Title: Field(FieldName.Title)}
        self.optionalFields.update({FieldName.Author: Author(),
                                    FieldName.Howpublished: Field(FieldName.Howpublished),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Year: Year(),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
    
    def generateKey(self):
        key = self.getField(FieldName.Key)
        if not key.isEmpty():
            key = Field.simplify(key.getValue())
        else:
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Author).getFirstLastName())
        return key + self.getField(FieldName.Year).getYear()
        
    
class Inbook(Book):
    """
    A part of a book, which may be a chapter (or section or whatever) and/or a range of pages.
    """
    def __init__(self):
        super(Inbook, self).__init__()
        self.entryType = 'INBOOK'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Editor: Editor(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.Publisher: Field(FieldName.Publisher),
                                FieldName.Chapter: Field(FieldName.Chapter),
                                FieldName.Pages: Pages(),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Series: Field(FieldName.Series),
                                    FieldName.Type: Field(FieldName.Type),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Edition: Field(FieldName.Edition),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    def validate(self):
        chapter_pages_check = (self.requiredFields[FieldName.Chapter].isEmpty() or self.requiredFields[FieldName.Chapter].isEmpty())
        return super(Inbook, self).validate() and chapter_pages_check
        
    
class Incollection(Entry):
    """
    A part of a book having its own title.
    """
    def __init__(self):
        super(Incollection, self).__init__()
        self.entryType = 'INCOLLECTION'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.BookTitle: Field(FieldName.BookTitle),
                                FieldName.Publisher: Field(FieldName.Publisher),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Editor: Editor(),
                                    FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Series: Field(FieldName.Series),
                                    FieldName.Type: Field(FieldName.Type),
                                    FieldName.Chapter: Field(FieldName.Chapter),
                                    FieldName.Pages: Pages(),
                                    FieldName.Edition: Field(FieldName.Edition),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    
class Inproceedings(Entry):
    """
    An article in a conference proceedings.
    """
    def __init__(self):
        super(Inproceedings, self).__init__()
        self.entryType = 'INPROCEEDINGS'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.BookTitle: Field(FieldName.BookTitle),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Editor: Editor(),
                                    FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Series: Field(FieldName.Series),
                                    FieldName.Pages: Pages(),
                                    FieldName.Organization: Organization(),
                                    FieldName.Publisher: Field(FieldName.Publisher),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    def toHtmlACM(self):
        # Capital letters are already between {}
        try:
            authors = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Author)))
            title = Field.toHTML(self.getFieldValue(FieldName.Title))
            booktitle = Field.toHTML(self.getFieldValue(FieldName.BookTitle))
            year = Field.toHTML(self.getFieldValue(FieldName.Year))
            editor = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Editor)))
            volume = Field.toHTML(self.getFieldValue(FieldName.Volume))
            number = Field.toHTML(self.getFieldValue(FieldName.Number))
            series = Field.toHTML(self.getFieldValue(FieldName.Series))
            pages = Field.toHTML(self.getFieldValue(FieldName.Pages))
            organization = Field.toHTML(self.getFieldValue(FieldName.Organization))
            publisher = Field.toHTML(self.getFieldValue(FieldName.Publisher))
            address = Field.toHTML(self.getFieldValue(FieldName.Address))
            month = Field.toHTML(self.getFieldValue(FieldName.Month))
            
            html = self.getHtmlHeader()
            html += '''<p><span style="font-variant:small-caps">{0}</span> {1}. In <i>{2}</i>'''
            html = html.format(authors, title, booktitle)
            if organization:
                html += ''', %s''' % organization
            html += ''' ('''
            if address:
                html += '''%s, ''' % address
            if month:
                html += '''%s ''' % month
            html += '''%s)''' % year
            if editor:
                html += ''', %s, Eds.''' %  editor
            if volume:
                html += ''', vol. %s''' % volume
            elif number:
                html += ''', %s''' % number
            if series:
                html += ''' of <i>%s</i>''' % series
            if publisher:
                html += ''', %s''' % publisher
            if pages:
                html += ''', pp. %s''' % pages
            html += '.</p>'
            
            return html
        except:
            raise Exception('Failed to generate ACM style.')
        
    
class Conference(Inproceedings):
    """
    An article in a conference proceedings.
    @deprecated: The same as INPROCEEDINGS, included for Scribe compatibility.
    """
    def __init__(self):
        super(Conference, self).__init__()
        self.entryType = 'CONFERENCE'
        
    
class Manual(Entry):
    """
    Technical documentation.
    """
    def __init__(self):
        super(Manual, self).__init__()
        self.entryType = 'MANUAL'
        self.requiredFields = { FieldName.Title: Field(FieldName.Title)}
        self.optionalFields.update({FieldName.Author: Author(),
                                    FieldName.Organization: Organization(),
                                    FieldName.Edition: Field(FieldName.Edition),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Year: Year(),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
    
    def generateKey(self):
        key = self.getField(FieldName.Key)
        if not key.isEmpty():
            key = Field.simplify(key.getValue())
        elif not self.getField(FieldName.Author).isEmpty():
            key = Field.simplify(self.getField(FieldName.Author).getFirstLastName())
        elif not self.getField(FieldName.Organization).isEmpty():
            key = Field.simplify(self.getField(FieldName.Organization).getFirstWord())
        return key + self.getField(FieldName.Year).getYear()
        
    
class Misc(Entry):
    """
    Document of any other type.
    """
    def __init__(self):
        super(Misc, self).__init__()
        self.entryType = 'MISC'
        self.optionalFields.update({FieldName.Author: Author(),
                                    FieldName.Title: Field(FieldName.Title),
                                    FieldName.Howpublished: Field(FieldName.Howpublished),
                                    FieldName.Year: Year(),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    
class Phdthesis(Entry):
    """
    A Ph.D. thesis.
    """
    def __init__(self):
        super(Phdthesis, self).__init__()
        self.entryType = 'PHDTHESIS'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.School: Field(FieldName.School),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Type: Field(FieldName.Type),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    def toHtmlACM(self):
        # Capital letters are already between {}
        try:
            authors = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Author)))
            title = Field.toHTML(self.getFieldValue(FieldName.Title))
            school = Field.toHTML(self.getFieldValue(FieldName.School))
            year = Field.toHTML(self.getFieldValue(FieldName.Year))
            _type = Field.toHTML(self.getFieldValue(FieldName.Type))
            address = Field.toHTML(self.getFieldValue(FieldName.Address))
            month = Field.toHTML(self.getFieldValue(FieldName.Month))
            
            html = self.getHtmlHeader()
            html += '''<p><span style="font-variant:small-caps">{0}</span> <i>{1}</i>. '''
            html = html.format(authors, title)
            if _type:
                html += '''%s, ''' % _type
            html += '''%s''' % school
            if address:
                html += ''', %s''' % address
            if month:
                html += ''', %s''' % month
            html += ''' %s''' % year
            html += '.</p>'
            
            return html
        except:
            raise Exception('Failed to generate ACM style.')
        
    
class Mastersthesis(Phdthesis):
    """
    A Master's thesis.
    """
    def __init__(self):
        super(Mastersthesis, self).__init__()
        self.entryType = 'MASTERSTHESIS'

    
class Proceedings(Entry):
    """
    The proceedings of a conference.
    """
    def __init__(self):
        super(Proceedings, self).__init__()
        self.entryType = 'PROCEEDINGS'
        self.requiredFields = { FieldName.Title: Field(FieldName.Title),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Editor: Editor(),
                                    FieldName.Volume: Field(FieldName.Volume),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Series: Field(FieldName.Series),
                                    FieldName.Organization: Organization(),
                                    FieldName.Publisher: Field(FieldName.Publisher),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
    
    def generateKey(self):
        key = self.getField(FieldName.Key)
        if not key.isEmpty():
            key = Field.simplify(key.getValue())
        elif not self.getField(FieldName.Editor).isEmpty():
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Editor).getFirstLastName())
        elif not self.getField(FieldName.Organization).isEmpty():
            # First author's last name (no {}, no spaces) concatenated with year
            key = Field.simplify(self.getField(FieldName.Organization).getFirstWord())
        return key + self.getField(FieldName.Year).getYear()


class Techreport(Entry):
    """
    A report published by a school or other institution, usually numbered within a series.
    """
    def __init__(self):
        super(Techreport, self).__init__()
        self.entryType = 'TECHREPORT'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.Institution: Field(FieldName.Institution),
                                FieldName.Year: Year()}
        self.optionalFields.update({FieldName.Type: Field(FieldName.Type),
                                    FieldName.Number: Field(FieldName.Number),
                                    FieldName.Address: Field(FieldName.Address),
                                    FieldName.Month: Field(FieldName.Month),
                                    FieldName.Note: Field(FieldName.Note)})
        
    def toHtmlACM(self):
        # Capital letters are already between {}
        try:
            authors = Field.toHTML(Entry.getACMContributors(self.getField(FieldName.Author)))
            title = Field.toHTML(self.getFieldValue(FieldName.Title))
            institution = Field.toHTML(self.getFieldValue(FieldName.Institution))
            year = Field.toHTML(self.getFieldValue(FieldName.Year))
            _type = Field.toHTML(self.getFieldValue(FieldName.Type))
            number = Field.toHTML(self.getFieldValue(FieldName.Number))
            address = Field.toHTML(self.getFieldValue(FieldName.Address))
            month = Field.toHTML(self.getFieldValue(FieldName.Month))
            
            html = self.getHtmlHeader()
            html += '''<p><span style="font-variant:small-caps">{0}</span> {1}. '''
            html = html.format(authors, title)
            if _type:
                html += '''%s, ''' % _type
            if number:
                html += '''%s, ''' % number
            html += '''%s, ''' % institution
            if address:
                html += '''%s, ''' % address
            if month:
                html += '''%s ''' % month
            html += '''%s''' % year
            html += '.</p>'
            
            return html
        except:
            raise Exception('Failed to generate ACM style.')

    
class Unpublished(Entry):
    """
    A report published by a school or other institution, usually numbered within a series.
    """
    def __init__(self):
        super(Unpublished, self).__init__()
        self.entryType = 'UNPUBLISHED'
        self.requiredFields = { FieldName.Author: Author(),
                                FieldName.Title: Field(FieldName.Title),
                                FieldName.Note: Field(FieldName.Note)}
        self.optionalFields.update({FieldName.Year: Year(),
                                    FieldName.Month: Field(FieldName.Month)})
