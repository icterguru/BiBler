from gui.app_interface import EntryListColumn

class FieldName:
    Address = 'address'
    Annote = 'annote'
    Author = 'author'
    BookTitle = 'booktitle'
    Chapter = 'chapter'
    Crossref = 'crossref'
    Edition = 'edition'
    Editor = 'editor'
    Howpublished = 'howpublished'
    Institution = 'institution'
    Journal = 'journal'
    Key = 'key'
    Month = 'month'
    Note = 'note'
    Number = 'number'
    Organization = 'organization'
    Pages = 'pages'
    Publisher = 'publisher'
    School = 'school'
    Series = 'series'
    Title = 'title'
    Type = 'type'
    Volume = 'volume'
    Year = 'year'
    Paper = 'paper'     # not part of the BibTeX standard
    Comment = 'comment' # not part of the BibTeX standard
    
    @staticmethod
    def toEntryListColumn(field):
        if field == FieldName.Author: return EntryListColumn.AUTHOR
        elif field == FieldName.Paper: return EntryListColumn.PAPER
        elif field == FieldName.Title: return EntryListColumn.TITLE
        elif field == FieldName.Year: return EntryListColumn.YEAR
        else:
            return field
    
    @staticmethod
    def fromEntryListColumn(column):
        if column == EntryListColumn.AUTHOR: return FieldName.Author
        elif column == EntryListColumn.PAPER: return FieldName.Paper
        elif column == EntryListColumn.TITLE: return FieldName.Title
        elif column == EntryListColumn.YEAR: return FieldName.Year
        else:
            raise Exception('The column is not an EntryColumnList.')
    
    @staticmethod
    def getAllFieldNames():
        return [FieldName.Address, FieldName.Annote, FieldName.Author, FieldName.BookTitle, FieldName.Crossref,
                FieldName.Chapter, FieldName.Edition, FieldName.Editor, FieldName.Howpublished, FieldName.Institution,
                FieldName.Journal, FieldName.Key, FieldName.Month, FieldName.Note, FieldName.Number,
                FieldName.Organization, FieldName.Pages, FieldName.Publisher, FieldName.School, FieldName.Series,
                FieldName.Title, FieldName.Type, FieldName.Volume, FieldName.Year, FieldName.Paper, FieldName.Comment]
    