
import re
from entry import Article, Book, Inproceedings, Phdthesis, Techreport, Booklet, Inbook, Incollection, Conference, Manual, Mastersthesis, Misc, Proceedings, Unpublished, EmptyEntry

class BibTeXParser(object):
    def __init__(self, bibtex):
        self.bibtex = bibtex.strip().replace('\n', ' ')         # remove all spaces and new lines
        self.bibtex = re.sub('=\s*\"', '= {', self.bibtex)      # replace all double quotes that delimit the beginning of a field value
        self.bibtex = re.sub('\"\s*,', '},', self.bibtex)       # replace all double quotes that delimit the end of a field value
        self.re_header = re.compile("""\s*@(\w+)\s*[({]\s*(\w*)\s*""", re.DOTALL)
        
    def parse(self):
        # 1. Get the type of entry
        if not self.bibtex:
            return None
        entry = None
        header = self.re_header.match(self.bibtex)
        if not header:
            raise Exception('Invalid BibTeX.')
        t = header.group(1)
        if not t:
            return None
        elif t.lower() == 'article':
            entry = Article()
        elif t.lower() == 'book':
            entry = Book()
        elif t.lower() == 'inproceedings':
            entry = Inproceedings()
        elif t.lower() == 'phdthesis':
            entry = Phdthesis()
        elif t.lower() == 'techreport':
            entry = Techreport()
        elif t.lower() == 'booklet':
            entry = Booklet()
        elif t.lower() == 'inbook':
            entry = Inbook()
        elif t.lower() == 'incollection':
            entry = Incollection()
        elif t.lower() == 'conference':
            entry = Conference()
        elif t.lower() == 'manual':
            entry = Manual()
        elif t.lower() == 'mastersthesis':
            entry = Mastersthesis()
        elif t.lower() == 'misc':
            entry = Misc()
        elif t.lower() == 'proceedings':
            entry = Proceedings()
        elif t.lower() == 'unpublished':
            entry = Unpublished()
        else:
            return EmptyEntry()  
        # 2. Get the key
        entry.setKey(header.group(2))        
        # 3. Get all fields
        for field in entry.getAllFields():
            value = self.findField(field)
            entry.setField(field, value)
            entry.formatField(field)
        return entry
        
    def findField(self, field):
        sep = '{'
        inv_sep = '}'
        result = re.findall(""",\s*(""" + field + """)\s*=\s*\{\s*(.*)\s*\}\s*,?""", self.bibtex, re.DOTALL)
        if len(result) == 0 or len(result[0]) != 2:
            return ''
        value = self.__parseNested(sep + result[0][1] + inv_sep, sep, inv_sep, 0)
        if not value:
            return ''
        return re.sub("""\s+""", ' ', value)
    
    def __parseNested(self, s, separator, inv_separator, level):
        stack = []
        for i,_ in enumerate(s):
            if s[i:i+len(separator)] == separator and not (s[i:i+len(inv_separator)] == inv_separator):
                stack.append(i)
            elif s[i:i+len(inv_separator)] == inv_separator and stack:
                start = stack.pop()
                if len(stack) == level:
                    return s[start + 1: i]

if __name__ == '__main__':
    from UserInterface import UserInterface
    ui = UserInterface()
    from testApplication import oracle
    for e in oracle.valid_authors: 
        b = BibTeXParser(e.getBibTeX()).parse()
        print b
        i = ui.addEntry(e.getBibTeX())
        original = ui.getBibTeX(i)
        ui.updateEntry(i, b.toBibTeX())
        new = ui.getBibTeX(i)
        print original
        print original == new