import re
from field_name import FieldName

class Field(object):
    def __init__(self, name, value=''):
        self.name = name
        self.value = value
    
    def isEmpty(self):
        return self.value == ''
        
    def getName(self):
        return self.value
        
    def getValue(self):
        return self.value
        
    def setValue(self, value):
        self.value = value
        
    def format(self):
        pass
    
    @staticmethod
    def simplify(value):
        chars = dict()
        chars["{\\ss}"] = 'ss'
        chars["\\o"] = 'o'
        for i in range(ord('A'), ord('Z')) + range(ord('a'), ord('z')):
            chars["{\\c%s}" % chr(i)] = '%s' % chr(i)
            chars["\\r{%s}" % chr(i)] = '%s' % chr(i)
            chars["{\\'%s}" % chr(i)] = '%s' % chr(i)
            chars["{\\`%s}" % chr(i)] = '%s' % chr(i)
            chars["{\\\"%s}" % chr(i)] = '%s' % chr(i)
            chars["{\\^%s}" % chr(i)] = '%s' % chr(i)
            chars["\\~{%s}" % chr(i)] = '%s' % chr(i)
        for i in chars.iterkeys():
            value = value.replace(i, chars[i])
        value = value.replace('[', '')
        value = value.replace(']', '')
        return Field.__clean(value)
        
    @staticmethod
    def toHTML(value):
        chars = dict()
        chars["{\\ss}"] = '&szlig;'
        chars["\\o"] = '&oslash;'
        chars["{\\&}"] = '&'
        for i in range(ord('A'), ord('Z')) + range(ord('a'), ord('z')):
            chars["{\\c%s}" % chr(i)] = '&%scedil;' % chr(i)
            chars["\\r{%s}" % chr(i)] = '&%sring;' % chr(i)
            chars["{\\'%s}" % chr(i)] = '&%sacute;' % chr(i)
            chars["{\\`%s}" % chr(i)] = '&%sgrave;' % chr(i)
            chars["{\\\"%s}" % chr(i)] = '&%suml;' % chr(i)
            chars["{\\^%s}" % chr(i)] = '&%scirc;' % chr(i)
            chars["\\~{%s}" % chr(i)] = '&%stilde;' % chr(i)
        for i in chars.iterkeys():
            value = value.replace(i, chars[i])
        value = value.replace('[', '')
        value = value.replace(']', '')
        value = value.replace('--', '&#8212;')
        return Field.__clean(value)      
    
    @staticmethod
    def __clean(value):
        value = value.replace('{', '')
        value = value.replace('}', '')
        value = value.replace('[', '')
        value = value.replace(']', '')
        value = value.replace('\\em', '')
        value = value.replace('\\it', '')
        value = value.replace('\\url', '')
        return value


class Contributor(object):
    def __init__(self, last, first='', von='', jr=''):
        self.first_name = first.strip()
        self.last_name = last.strip()
        self.preposition = von.strip()
        self.suffix = jr.strip()
    
    def __str__(self):
        s = ''
        if self.preposition:
            s += self.preposition + ' '
        if self.last_name:
            s += self.last_name
        if self.suffix:
            s += ', ' + self.suffix
        if self.first_name:
            s += ', ' + self.first_name
        return s

class ContributorField(Field):
    def __init__(self, name, value=''):
        super(ContributorField, self).__init__(name, value)
        self.contributors = []
        self.re_von_Last_Jr_First = re.compile("""([^A-Z\{\}]*)\s*([^,]+)\s*,\s*([^,]*)\s*,\s*(.*)""", re.DOTALL)
        self.re_von_Last_First = re.compile("""([^A-Z\{\}]*)\s*([^,]+)\s*,\s*(.*)""", re.DOTALL)
    
    def getContributors(self):
        return self.contributors
        
    def format(self):
        people = self.value
        if not people:
            return
        etal = people.find('et al.')
        if etal < 0:
            etal = people.find('and others')
        if etal >= 0:
            people = people[:etal]
        people = people.split(' and ')
        for person in people:
            name = self.re_von_Last_Jr_First.match(person)
            if name:
                # von Last, Jr, First
                self.contributors.append(Contributor(last=name.group(2), first=name.group(4), von=name.group(1), jr=name.group(3)))
            else:
                name = self.re_von_Last_First.match(person)
                if name:
                    # von Last, First
                    self.contributors.append(Contributor(last=name.group(2), first=name.group(3), von=name.group(1)))
                else:
                    # First von Last 
                    person = person.split()
                    prepIx = -1
                    for i,name in enumerate(person):
                        if name[0].islower():
                            prepIx = i
                            break
                    if prepIx < 0:
                        self.contributors.append(Contributor(last=person[-1], first=' '.join(person[:-1])))
                    elif prepIx == len(person) - 1:
                        raise Exception('Incorrect author name: missing last name.')
                    else:
                        lastIx = prepIx
                        for i,name in enumerate(person[prepIx + 1:]):
                            if name[0].isupper():
                                lastIx = i + prepIx + 1
                                break
                        self.contributors.append(Contributor(last=' '.join(person[lastIx:]), first=' '.join(person[:prepIx]), von=' '.join(person[prepIx:lastIx])))
        self.value = ' and '.join([str(c) for c in self.contributors])
    
    def getFirstLastName(self):
        if not self.contributors:
            raise Exception('No author or editor name found.')
        return Field.simplify(self.contributors[0].last_name.replace(' ', ''))
        
    
class Author(ContributorField):
    def __init__(self, value = ''):
        super(Author, self).__init__(FieldName.Author, value)
        
    
class Editor(ContributorField):
    def __init__(self, value = ''):
        super(Editor, self).__init__(FieldName.Editor, value)


class Organization(Field):
    def __init__(self, value = ''):
        super(Organization, self).__init__(FieldName.Organization, value)
    
    def getFirstWord(self):
        if len(self.value) == 0:
            return ''
        return self.value.split()[0]
        
    
class Pages(Field):
    def __init__(self, value = ''):
        super(Pages, self).__init__(FieldName.Pages, value)
        self.re_dashes = re.compile("""-+""")
        
    def format(self):
        self.value = self.value.replace(' ', '')
        self.value = self.re_dashes.sub('--', self.value)


class Year(Field):
    def __init__(self, value = ''):
        super(Year, self).__init__(FieldName.Year, value)
    
    def getYear(self):
        if len(self.value) >= 4:
            return self.value[-4:]
        else:
            return ''
