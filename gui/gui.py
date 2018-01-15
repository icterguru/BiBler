'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This module represents the graphical user interface of BiBler.
It should be used as an API that a statechart controller can invoke.

@group Main GUI class: MainWindow
@group Widgets: AboutBox, EditorTab, EntryEditor, EntryList, EntryPreviewer, EntryWidget, PreferencesDialog, SearchDialog, UserManualWindow
@sort: A*, E*, P*, S*, U*
'''

import wx
import wx.lib.mixins.listctrl as wxLC
import wx.html as wxHTML
import webbrowser
from utils import settings
from utils import resourcemgr
from app_interface import EntryListColumn

prefs = settings.Preferences()
"""
Load the preferences
"""
resMgr = resourcemgr.ResourceManager()
"""
Load the resource manager
"""

class EntryWidget(object):
    """
    A widget to control entries.
    """
    def __init__(self, rows, cols, behavior=None):
        """
        @type rows: L{int}
        @param rows: The number of rows of the C{wx.FlexGridSizer} of the widget.
        @type cols: L{int}
        @param cols: The number of columns of the C{wx.FlexGridSizer} of the widget.
        @type behavior: L{controller.Controller}
        @param behavior: The statechart controller that defines the behavior of this widget.
        """
        self.behavior = behavior
        self.sizer = wx.FlexGridSizer(rows=rows, cols=cols)
    
    def clear(self):
        """
        Clear the content of the widget.
        """
        raise NotImplemented()
    
    def getSizer(self):
        """
        Get the sizer of the L{EntryEditor}.
        @rtype: C{wx.FlexGridSizer}
        @return: The sizer.
        """
        return self.sizer

class EntryList(wx.ListCtrl, wxLC.ListCtrlAutoWidthMixin):
    """
    The list of entries.    
    It contains the 7 columns from L{gui.app_interface.EntryDict}: id, Paper, Type, Author, Title, Year, Key.
    @group Events: __on*
    @sort: __*, a*, d*, g*, G*, i*, r*, s*, u*
    
    """
    def __init__(self, parent, behavior):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window. Must be not C{None}.
        @type behavior: L{controller.Controller}
        @param behavior: The statechart controller that defines the behavior of this window.
        """
        wx.ListCtrl.__init__(self, parent, wx.NewId(),
                             style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER
                                    | wx.LC_HRULES | wx.LC_VRULES | wx.EXPAND)
        wxLC.ListCtrlAutoWidthMixin.__init__(self)
        
        self.behavior = behavior
        
        self.InsertColumn(0, "#", width=35)
        self.InsertColumn(1, "Paper", width=20)
        self.InsertColumn(2, "Type", width=100)
        self.InsertColumn(3, "Author", width=200)
        self.InsertColumn(4, "Title", width=500)
        self.InsertColumn(5, "Year", width=50)
        self.InsertColumn(6, "Key", width=100)
        self.setResizeColumn(3)
        self.setResizeColumn(4)
        self.setResizeColumn(5)
        self.paperImageList = wx.ImageList(16, 16)
        bitmap = wx.Bitmap(resMgr.getPaperImagePath(), wx.BITMAP_TYPE_PNG)
        self.paperImageList.Add(bitmap)
        self.AssignImageList(self.paperImageList, wx.IMAGE_LIST_SMALL) 
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.__onEntrySelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.__onEntryDeselected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onEntryDoubleClicked)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.__onColumnClicked)
        
    def __onEntrySelected(self, e):
        """
        Triggered when a row is clicked.
        @type e: C{wx.ListEvent}
        """
        self.behavior.entrySelected(self.getEntryId(e.GetIndex()))
        
    def __onEntryDeselected(self, e):
        """
        Triggered when the entry list is clicked, but not a on row.
        @type e: C{wx.ListEvent}
        """
        self.behavior.entryDeselected()
    
    def __onEntryDoubleClicked(self, e):
        """
        Triggered when a row is double-clicked.
        @type e: C{wx.ListEvent}
        """
        self.behavior.entryDoubleClicked(self.getEntryId(e.GetIndex()))
    
    def __onColumnClicked(self, e):
        """
        Triggered when the header of a column is clicked.
        @type e: C{wx.ListEvent}
        """
        col = e.GetColumn()
        if col == 0:
            self.behavior.colIdClicked()
        elif col == 1:
            self.behavior.colPaperClicked()
        elif col == 2:
            self.behavior.colTypeClicked()
        elif col == 3:
            self.behavior.colAuthorClicked()
        elif col == 4:
            self.behavior.colTitleClicked()
        elif col == 5:
            self.behavior.colYearClicked()
        elif col == 6:
            self.behavior.colKeyClicked()       
    
    def GetListCtrl(self):
        """
        Required by C{wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin}.
        """
        return self
    
    def getEntryId(self, row):
        """
        Returns the id of the entry on this row.
        @type row: C{int}
        @param row: The index of a row.
        @rtype: C{int}
        @return: The id of the entry.
        """
        return int(self.GetItem(row, 0).GetText())
    
    def isEntrySelected(self):
        """
        Check if a row is selected.
        @rtype: L{bool}
        @return: C{True} if a row is selected. C{False} otherwise.
        """
        return self.GetSelectedItemCount() > 0
    
    def selectEntryRow(self, entryId):
        """
        Select the row corresponding to the entry I{id}.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry.
        @raise Exception: If no entry was found.
        """
        index = self.FindItem(0, str(entryId))
        if index == wx.NOT_FOUND:
            raise Exception('Entry not found.')
        self.Select(index)
        return True
        
    def unselectEntryRow(self):
        """
        Ensure no row is selected.
        """
        self.Select(-1)
        return True
    
    def displayEntries(self, entryList):
        """
        Show the entry list, one row per entry.
        @type entryList: L{list} of L{EntryDict}
        @param entryList: The list of entries to show.
        """
        self.DeleteAllItems()
        for entry in entryList:
            self.addEntryRow(entry)
        return True
    
    def addEntryRow(self, entryDict):
        """
        Add a new row filled with the data for an entry.
        @type entryDict: L{EntryDict}
        @param entryDict: The dictionary representation of an entry.
        """
        row = self.Append(self.__entryDictToRowTuple(entryDict))
        self.showPDFIcon(row, entryDict[EntryListColumn.PAPER])
        return True
    
    def updateSelectedEntryRow(self, entryDict):
        """
        Update the columns of a row with the data provided.
        @type entryDict: L{EntryDict}
        @param entryDict: The dictionary representation of an entry.
        @raise Exception: If no row was selected.
        """
        row = self.GetFirstSelected()
        if row < 0: raise Exception('No entry selected.')
        data = self.__entryDictToRowTuple(entryDict)
        for i in xrange(len(data)):
            self.SetStringItem(row, i, data[i])
        self.showPDFIcon(row, entryDict[EntryListColumn.PAPER])
        return True
    
    def removeEntryRow(self, entryId):
        """
        Remove the row corresponding to the entry I{id}.
        @type entryId: L{int}
        @param entryId: The I{id} of the entry.
        @raise Exception: If no entry was found.
        """
        index = self.FindItem(0, str(entryId))
        if index == wx.NOT_FOUND:
            raise Exception('Entry not found.')
        self.DeleteItem(index)
        return True
    
    def showPDFIcon(self, row, data):
        """
        Display a PDF icon in the C{paper} column if C{data != ''}.
        @type row: L{int}
        @param row: The index of a row.
        @type data: L{str}
        @param data: The uri of the paper.
                        
        """
        if data != '':
            self.SetItemColumnImage(row, 1, 0)
            self.SetStringItem(row, 1, '')    # only display the icon, so remove text
        else:
            self.SetItemColumnImage(row, 1, -1)
        return True
    
    def __entryDictToRowTuple(self, entryDict):
        """
        Converts an L{EntryDict} into a L{tuple}.
        The order of the data is the same as in L{EntryList}.
        In the case of multiple authors, the I{et al.} notation is used.
        @type entryDict: L{EntryDict}
        @param entryDict: The dictionary representation of an entry.
        @rtype: L{tuple}
        @return: The tuple representation of the C{entryDict}.
        """
        author = str(entryDict[EntryListColumn.AUTHOR])
        if 'and' in author:
            author = author.split(',')[0] + ' et al.'
        else:
            author = author.split(',')[0]
        return (str(entryDict[EntryListColumn.ID]), str(entryDict[EntryListColumn.PAPER]), str(entryDict[EntryListColumn.TYPE]),
               author, str(entryDict[EntryListColumn.TITLE]), str(entryDict[EntryListColumn.YEAR]), str(entryDict[EntryListColumn.KEY]))

class EditorTab(wx.Panel):
    """
    A tab in the L{EntryEditor}.
    """
    def __init__(self, parent):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window. Must be not C{None}.
        """
        wx.Panel.__init__(self, parent, wx.NewId())

class EntryEditor(EntryWidget):
    """
    The editor of a reference.
    @group Events: __on*
    @sort: __*, c*, d*, e*, s*
    """
    def __init__(self, parent, behavior):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window. Must be not C{None}.
        @type behavior: L{controller.Controller}
        @param behavior: The statechart controller that defines the behavior
        """
        EntryWidget.__init__(self, 3, 1, behavior)
        self.title = wx.StaticText(parent, wx.NewId(), 'Edit fields')
        self.tabs = wx.Notebook(parent, style=wx.NB_TOP)
        
        self.bibtexTab = EditorTab(self.tabs)
        self.bibtexEditor = wx.TextCtrl(self.bibtexTab, wx.NewId(),
                                  style=wx.TE_MULTILINE | wx.TE_LINEWRAP | wx.TE_AUTO_SCROLL)
        self.bibtexEditor.SetFont(wx.Font(pointSize=11, family=wx.FONTFAMILY_MODERN,
                                    style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))
        self.bibtexEditor.Bind(wx.EVT_TEXT, self.__onTextChangedInEditor)
        
        self.tabs.InsertPage(0, self.bibtexTab, "BibTeX", True)
        
        self.updateButton = wx.Button(parent, wx.NewId(), 'Update')
        self.updateButton.Disable()
        self.updateButton.Bind(wx.EVT_BUTTON, self.__onUpdateButtonClick)
        
        tabSizer = wx.FlexGridSizer(rows=1, cols=1)
        tabSizer.AddGrowableCol(0, 1)
        tabSizer.AddGrowableRow(0, 1)
        tabSizer.Add(self.bibtexEditor, 1, wx.EXPAND)
        updateButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        updateButtonSizer.Add((0, 0), 1, wx.EXPAND)
        updateButtonSizer.Add(self.updateButton)
        self.bibtexTab.SetSizerAndFit(tabSizer)
        self.sizer.AddGrowableCol(0, 1)
        self.sizer.AddGrowableRow(1, 1)
        self.sizer.Add(self.title)
        self.sizer.Add(self.tabs, 1, wx.EXPAND)
        self.sizer.Add(updateButtonSizer, 1, wx.EXPAND)
    
    def __onTextChangedInEditor(self, e):
        """
        Triggered every time the text is change.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.textChangedInEditor(e.GetString())
        
    def __onUpdateButtonClick(self, e):
        """
        Triggered when the Update button is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.updateButtonClicked(self.bibtexEditor.GetValue())
    
    def enableUpdateButton(self):
        """
        Enable the Update button.
        """
        self.updateButton.Enable(True)
        return True
    
    def disableUpdateButton(self):
        """
        Disable the Update button.
        """
        self.updateButton.Enable(False)
        return True
    
    def clear(self):
        """
        Remove all the text from the editor.
        """
        self.bibtexEditor.Clear()
        return True
    
    def setBibtex(self, data):
        """
        Replace text in the BibTeX editor with C{data}.
        @type data: L{str}
        @param data: The text to write.
        """
        self.bibtexEditor.Clear()
        self.bibtexEditor.WriteText(data)
        self.bibtexEditor.SetInsertionPoint(0)  # set cursor at the beginning of the text
        return True

class EntryPreviewer(EntryWidget):
    """
    The editor of a reference.
    """
    def __init__(self, parent):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window. Must be not C{None}.
        """
        EntryWidget.__init__(self, 2, 1, behavior=None)
        self.title = wx.StaticText(parent, wx.NewId(), 'Preview reference')
        self.htmlPreviewer = wxHTML.HtmlWindow(parent, style=wxHTML.HW_SCROLLBAR_NEVER)
        
        self.sizer = wx.FlexGridSizer(rows=2, cols=1)
        self.sizer.AddGrowableCol(0, 1)
        self.sizer.AddGrowableRow(1, 1)
        self.sizer.Add(self.title)
        self.sizer.Add(self.htmlPreviewer, 1, wx.EXPAND)
    
    def clear(self):
        """
        Remove all content.
        """
        self.htmlPreviewer.SetPage('')
        return True
    
    def display(self, content):
        """
        Display the content.
        @type content: L{str}
        @param content: The HTML text to display.
        """
        self.htmlPreviewer.SetPage(content)
        return True

class HTMLDialog(wx.Dialog):
    """
    A dialog displaying HTML content.
    """
    def __init__(self, parent, title, source, size=(420, 200)):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window.
        @type title: C{str}
        @param title: The title of the dialog.
        @type source: C{str}
        @param source: The path to the source of the HTML.
        @type size: C{tuple}
        @param size: The width and height of the dialog.
        """
        wx.Dialog.__init__(self, parent, wx.NewId(), title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = wxHTML.HtmlWindow(self, wx.NewId(), size=size)
        hwin.LoadPage(source)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class HTMLWindow(wx.Frame):
    """
    A window displaying HTML content.
    """
    def __init__(self, parent, title, source):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window.
        @type title: C{str}
        @param title: The title of the dialog.
        @type source: C{str}
        @param source: The path to the source of the HTML.
        """
        wx.Frame.__init__(self, parent, wx.NewId(), title=title)
        
        content = wxHTML.HtmlWindow(self, wx.NewId())
        content.LoadPage(source)

class ActionCancelDialog(wx.Dialog):
    """
    A generic dialog with one customizable action button and one cancel button.
    The L{performAction} method can be overridden to customize the action of the action button.
    @group Events: __on*
    @sort: __*, g*, p*, s*
    """
    def __init__(self, parent, title, actionButtonLabel='OK'):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window.
        """
        wx.Dialog.__init__(self, parent, wx.NewId(), title=title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, wx.NewId())
        self.actionButton = wx.Button(self.panel, label=actionButtonLabel)
        self.actionButton.Bind(wx.EVT_BUTTON, self.__onActionButtonClicked)
        self.cancelButton = wx.Button(self.panel, label="Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.__onCancelClicked)
        
        self.__isSizerSet = False
    
    def setSizer(self, sizer):
        """
        Set the sizer that goes on top of the buttons.
        @type sizer: C{wx.Sizer}
        @param sizer: The sizer
        """
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(self.actionButton, 0, wx.ALL, 5)
        bottomSizer.Add(self.cancelButton, 0, wx.ALL, 5)
        mainSizer.Add(sizer)
        mainSizer.Add(bottomSizer)
        self.panel.SetSizerAndFit(mainSizer)
        mainSizer.Fit(self)
        self.__isSizerSet = True
    
    def ShowModal(self):
        """
        @raise Exception: If L{setSizer} was not called before.
        """
        if self.__isSizerSet:
            return wx.Dialog.ShowModal(self)
        else:
            raise Exception('setSizer must be called before ShowModal')
    
    def getPanel(self):
        """
        @return: The main panel of the dialog.
        @rtype: C{wx.Panel}
        """
        return self.panel
    
    def __onActionButtonClicked(self, e):
        """
        Triggered when the action button is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.performAction(e)
        self.EndModal(wx.ID_OK)
    
    def __onCancelClicked(self, e):
        """
        Triggered when Cancel is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.EndModal(wx.ID_CANCEL)
    
    def performAction(self, e):
        """
        Abstract method that performs the action.
        """
        pass
        
class PreferencesDialog(ActionCancelDialog):
    """
    The Preferences dialog.
    It allows to change the preferences of the tool.
    @group Events: __on*
    @sort: __*
    """
    def __init__(self, parent):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window.
        """
        ActionCancelDialog.__init__(self, parent, title="Preferences")
        
        self.bibStyle = None
        styleLabel = wx.StaticText(self.panel, wx.NewId(), 'Bibliography style:')
        self.acmRadio = wx.RadioButton(self.panel, label="ACM", style= wx.RB_GROUP)
        self.ieeeRadio = wx.RadioButton(self.panel, label="IEEE")
        self.acmRadio.Bind(wx.EVT_RADIOBUTTON, self.__onACMRadioClicked)
        self.ieeeRadio.Bind(wx.EVT_RADIOBUTTON, self.__onIEEERadioClicked)
        if prefs.bibStyle == settings.BibStyle.ACM:
            self.acmRadio.SetValue(True)
            self.ieeeRadio.SetValue(False)
            self.bibStyle = settings.BibStyle.ACM
        else:
            self.acmRadio.SetValue(False)
            self.ieeeRadio.SetValue(True)
            self.bibStyle = settings.BibStyle.IEEE

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(styleLabel, 0, wx.ALL, 5)
        sizer.Add(self.acmRadio, 0, wx.ALL, 5)
        sizer.Add(self.ieeeRadio, 0, wx.ALL, 5)
        self.setSizer(sizer)
    
    def performAction(self, e):
        """
        Triggered when OK is clicked.
        Stores the preferences in L{prefs}
        @type e: C{wx.CommandEvent}
        """
        prefs.bibStyle = self.bibStyle
    
    def __onACMRadioClicked(self, e):
        """
        Triggered when ACM radio button is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.bibStyle = settings.BibStyle.ACM
    
    def __onIEEERadioClicked(self, e):
        """
        Triggered when IEEE radio button is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.bibStyle = settings.BibStyle.IEEE

class SearchDialog(ActionCancelDialog):
    """
    The Search dialog.
    It allows to search for a query in the list of entries.
    @group Events: __on*
    @sort: __*, g*
    """
    def __init__(self, parent):
        """
        @type parent: C{wx.Window}
        @param parent: The parent window.
        """
        ActionCancelDialog.__init__(self, parent, title="Search", actionButtonLabel="Filter")
        
        searchLabel = wx.StaticText(self.panel, wx.NewId(), 'Query:')
        self.query = wx.TextCtrl(self.panel, wx.NewId(), size=(200, -1))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(searchLabel, 0, wx.ALL, 5)
        sizer.Add(self.query, 0, wx.ALL, 5)
        self.setSizer(sizer)
        self.query.SetFocus()

    def getSearchQuery(self):
        """
        Get the query entered.
        """
        return self.query.GetValue()

class MainWindow(wx.Frame):
    """
    Main window of the application.
    @group Events: __on*
    @sort: __*, a*, c*, d*, e*, i*, o*, p*, r*, s*, u*
    """
    def __init__(self, behavior, maximize=False):
        """
        @type behavior: controller.Controller
        @param behavior: The statechart controller that defines the behavior of this window
        """
        wx.Frame.__init__(self, None, wx.NewId())        
        # The statechart behavior
        self.behavior = behavior
        # The icon and title of the window
        self.SetTitle("BiBler - the simple bibliography management tool")
        self.SetIcon(wx.Icon(resMgr.getIconPath(), wx.BITMAP_TYPE_ICO))
        # A status bar at the bottom of the window
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(2)
        self.SetStatusWidths([-1, 50])
        self.updateStatusBarTotal(0)
        # A panel to hold all the controls
        panel = wx.Panel(self, wx.NewId())
        # In case the 'X' is clicked
        self.Bind(wx.EVT_CLOSE, self.__onExit)
        
        #####################
        # Create the menu bar
        #####################
        fileMenu = wx.Menu()
        menuOpen = fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl+O"," Open a BibTeX file")
        menuSave = fileMenu.Append(wx.ID_SAVE,"&Save\tCtrl+S"," Save the database")
        menuSaveAs = fileMenu.Append(wx.ID_SAVEAS,"Save As"," Save the database to a BibTeX file")
        fileMenu.AppendSeparator()
        menuImport = fileMenu.Append(wx.NewId(), "&Import from file\tCtrl+I"," Import database from a file")
        menuExport = fileMenu.Append(wx.NewId(),"&Export to file\tCtrl+E"," Export database to a file")
        fileMenu.AppendSeparator()
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit\tAlt+F4"," Terminate the program")
        
        editMenu = wx.Menu()
        menuUndo = editMenu.Append(wx.ID_UNDO, "Undo\tCtrl+Z"," Undo last action")
        menuUndo.Enable(False)
        editMenu.AppendSeparator()
        menuSearch = editMenu.Append(wx.ID_FIND, "&Search\tCtrl+F"," Filter the bibliography with entries matching a query")
        menuClearFilter = editMenu.Append(wx.ID_CLEAR, "Clear Filter"," Clear the search results")
        menuClearFilter.Enable(False)
        editMenu.AppendSeparator()
        menuPreferences = editMenu.Append(wx.ID_PREFERENCES,"&Preferences"," Manage settings and preferences")
        
        referenceMenu = wx.Menu()
        menuAdd = referenceMenu.Append(wx.ID_ADD,"&Add"," Add a referenceMenu")
        menuDelete = referenceMenu.Append(wx.ID_DELETE,"&Delete"," Remove a referenceMenu")
        menuDelete.Enable(False)
        menuDuplicate = referenceMenu.Append(wx.ID_DUPLICATE, "&Duplicate"," Duplicate the selected reference")
        menuDuplicate.Enable(False)
        
        helpMenu = wx.Menu()
        menuManual = helpMenu.Append(wx.ID_HELP,"User &Manual"," The user manual")
        helpMenu.AppendSeparator()
        menuAbout = helpMenu.Append(wx.ID_ABOUT, "About &BiBler"," Information about this program")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(editMenu,"&Edit")
        menuBar.Append(referenceMenu,"&Reference")
        menuBar.Append(helpMenu,"&Help")
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.__onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.__onSave, menuSave)
        self.Bind(wx.EVT_MENU, self.__onSaveAs, menuSaveAs)
        self.Bind(wx.EVT_MENU, self.__onImport, menuImport)
        self.Bind(wx.EVT_MENU, self.__onExport, menuExport)
        self.Bind(wx.EVT_MENU, self.__onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.__onUndo, menuUndo)
        self.Bind(wx.EVT_MENU, self.__onSearch, menuSearch)
        self.Bind(wx.EVT_MENU, self.__onClearFilter, menuClearFilter)
        self.Bind(wx.EVT_MENU, self.__onPreferences, menuPreferences)
        self.Bind(wx.EVT_MENU, self.__onAdd, menuAdd)
        self.Bind(wx.EVT_MENU, self.__onDelete, menuDelete)
        self.Bind(wx.EVT_MENU, self.__onDuplicate, menuDuplicate)
        self.Bind(wx.EVT_MENU, self.__onManual, menuManual)
        self.Bind(wx.EVT_MENU, self.__onAbout, menuAbout)
        
        #####################
        # Create the widgets
        #####################
        
        self.entryList = EntryList(panel, self.behavior)
        self.editor = EntryEditor(panel, self.behavior)
        self.previewer = EntryPreviewer(panel)
                
        #####################
        # Layout the controls
        #####################
        mainSizer = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        mainSizer.AddGrowableCol(0, 1)
        mainSizer.AddGrowableRow(0, 5)
        mainSizer.AddGrowableRow(2, 2)
        bottomSizer = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        bottomSizer.AddGrowableCol(1, 1)
        bottomSizer.AddGrowableCol(3, 1)
        bottomSizer.AddGrowableRow(0, 1)
        bottomSizer.AddSpacer(5)
        bottomSizer.Add(self.editor.getSizer(), 1, wx.EXPAND)
        bottomSizer.AddSpacer(5)
        bottomSizer.Add(self.previewer.getSizer(), 1, wx.EXPAND)
        bottomSizer.AddSpacer(5)
        mainSizer.Add(self.entryList, 1, wx.EXPAND)
        mainSizer.AddSpacer(5)
        mainSizer.Add(bottomSizer, 1, wx.EXPAND)
        panel.SetSizerAndFit(mainSizer)
        mainSizer.Fit(self)
        
        if maximize:
            self.Maximize()
        
    def __onOpen(self, e):
        """
        Triggered when File>Open is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.openClicked()
        
    def __onSave(self, e):
        """
        Triggered when File>Save is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.saveClicked(settings.ExportFormat.BIBTEX)
        
    def __onSaveAs(self, e):
        """
        Triggered when File>Save As is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.saveAsClicked()
        
    def __onImport(self, e):
        """
        Triggered when File>Import is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.importClicked()
        
    def __onExport(self, e):
        """
        Triggered when File>Export is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.exportClicked()

    def __onExit(self, e):
        """
        Triggered when File>Exit or the 'X' at the top right of the window is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.exitClicked()
    
    def __onUndo(self, e):
        """
        Triggered when Edit>Undo is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.undoClicked()
        
    def __onSearch(self, e):
        """
        Triggered when Edit>Search is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.searchClicked()
    
    def __onClearFilter(self, e):
        """
        Triggered when Edit>Clear Filter is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.clearFilterClicked()
        
    def __onPreferences(self, e):
        """
        Triggered when Edit>Preferences is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.preferencesClicked()
        
    def __onAdd(self, e):
        """
        Triggered when Reference>Add is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.addClicked()
        
    def __onDelete(self, e):
        """
        Triggered when Reference>Delete is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.deleteClicked()
        
    def __onDuplicate(self, e):
        """
        Triggered when Reference>Duplicate is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.duplicateClicked()
        
    def __onManual(self, e):
        """
        Triggered when Help>User Manual is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.manualClicked()
        
    def __onAbout(self, e):
        """
        Triggered when Help>About BiBler is clicked.
        @type e: C{wx.CommandEvent}
        """
        self.behavior.aboutClicked()
    
    def start(self):
        """
        Launch the window.
        """
        self.Show(True)
    
    def exit(self):
        """
        Close the window.
        """
        self.Destroy()
    
    def setDirtyTitle(self):
        """
        Place a C{*} at the end of the title in the title bar. 
        """
        title = self.GetTitle()
        if title[-1] != '*':
            self.SetTitle(title + '*')
        return True
    
    def unsetDirtyTitle(self):
        """
        Remove the C{*} from the title in the title bar. 
        """
        title = self.GetTitle()
        if title[-1] == '*':
            self.SetTitle(title[:-1])
        return True
    
    def displayEntries(self, entryList):
        """
        Show the entries in the entry list.
        @type entryList: L{list} of L{EntryDict}
        @param entryList: The list of entries to show.
        """
        self.clearList()
        for entry in entryList:
            self.entryList.addEntryRow(entry)
        return True
    
    def updateSelectedEntryRow(self, entryDict):
        """
        See L{EntryList.updateSelectedEntryRow}.
        """
        return self.entryList.updateSelectedEntryRow(entryDict)
    
    def addNewEntryRow(self, entryDict):
        """
        See L{EntryList.addEntryRow}.
        """
        return self.entryList.addEntryRow(entryDict)
    
    def selectEntryRow(self, entryId):
        """
        See L{EntryList.selectEntryRow}.
        """
        return self.entryList.selectEntryRow(entryId)
    
    def isEntrySelected(self):
        """
        See L{EntryList.isEntrySelected}.
        """
        return self.entryList.isEntrySelected()
    
    def removeEntryRow(self, entryId):
        """
        See L{EntryList.removeEntryRow}.
        """
        return self.entryList.removeEntryRow(entryId)
    
    def unselectEntryRow(self):
        """
        See L{EntryList.unselectEntryRow}
        """
        return self.entryList.unselectEntryRow()
    
    def clearList(self):
        """
        Delete all rows of the entry list.
        """
        self.entryList.DeleteAllItems()
        return True
    
    def displayBibTexInEditor(self, data):
        """
        See L{EntryEditor.setBibtex}.
        """
        return self.editor.setBibtex(data)
    
    def clearEditor(self):
        """
        See L{EntryEditor.clear}.
        """
        return self.editor.clear()
    
    def clearPreviewer(self):
        """
        See L{EntryPreviewer.clear}.
        """
        return self.previewer.clear()
    
    def previewEntry(self, content):
        """
        See L{EntryPreviewer.display}.
        """
        return self.previewer.display(content)
    
    def updateStatusBar(self, msg):
        """
        Display a message in the left status bar.
        @type msg: L{str}
        @param msg: The message to display.
        """
        self.statusBar.SetStatusText(msg)
        return True
    
    def clearStatusBar(self):
        """
        Remove any message from the left status bar.
        """
        self.statusBar.SetStatusText('')
        return True
    
    def updateStatusBarTotal(self, total):
        """
        Display the total number of entries in the right status bar.
        @type total: L{int}
        @param total: The total number of entries.
        """
        self.SetStatusText(' Total: %s' % total, 1)
        return True
    
    def enableClearFilter(self):
        """
        Enable the Clear Filter menu.
        """
        self.GetMenuBar().FindItemById(wx.ID_CLEAR).Enable(True)
        return True
    
    def disableClearFilter(self):
        """
        Disable the Clear Filter menu.
        """
        self.GetMenuBar().FindItemById(wx.ID_CLEAR).Enable(False)
        return True
    
    def enableDelete(self):
        """
        Enable the Delete menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_DELETE).Enable(True)
        return True
    
    def disableDelete(self):
        """
        Disable the Delete menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_DELETE).Enable(False)
        return True
    
    def enableDuplicate(self):
        """
        Enable the Duplicate menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_DUPLICATE).Enable(True)
        return True
    
    def disableDuplicate(self):
        """
        Disable the Duplicate menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_DUPLICATE).Enable(False)
        return True
    
    def enableUndo(self):
        """
        Enable the Undo menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_UNDO).Enable(True)
        return True
    
    def disableUndo(self):
        """
        Disable the Undo menu.
        """
        self.GetMenuBar().FindItemById(wx.wx.ID_UNDO).Enable(False)
        return True
    
    def enableUpdateButton(self):
        """
        Enable the Update button.
        """
        return self.editor.enableUpdateButton()
    
    def disableUpdateButton(self):
        """
        Disable the Update button.
        """
        return self.editor.disableUpdateButton()
    
    def popupOpenDialog(self):
        """
        Open a dialog to select a BibTeX file to open.
        The title of the window will reflect the path to the file.
        """
        dlg = wx.FileDialog(self, "Open a bibliography file", prefs.defaultDir, "",
                            "BibTeX (*.bib)|*.bib",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.behavior.openFileSelected(path, settings.ImportFormat.BIBTEX)
            self.SetTitle('BiBler - ' + path)
            prefs.defaultDir = path
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupSaveDialog(self):
        """
        Open a dialog to select a BibTeX file to save to.
        The title of the window will reflect the path to the file.
        """
        dlg = wx.FileDialog(self, "Save the bibliography to a file", prefs.defaultDir, "",
                            "BibTeX (*.bib)|*.bib",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.behavior.saveFileSelected(path, settings.ExportFormat.BIBTEX)
            self.SetTitle('BiBler - ' + path)
            prefs.defaultDir = path
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupImportDialog(self):
        """
        Open a dialog to select a CSV file to import from.
        """
        dlg = wx.FileDialog(self, "Import a bibliography file", prefs.defaultDir, "",
                            "Comma-Separated Values (*.csv)|*.csv",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.behavior.importFileSelected(dlg.GetPath(), settings.ImportFormat.CSV)
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupExportDialog(self):
        """
        Open a dialog to select an HTML or CSV file to export to.
        """
        dlg = wx.FileDialog(self, "Export to a file", prefs.defaultDir, "",
                            "Web page (*.html)|*.html|Comma-Separated Values (*.csv)|*.csv",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            _format = None
            flt = dlg.GetFilterIndex()
            if flt == 0:
                _format = settings.ExportFormat.HTML
            else:
                _format = settings.ExportFormat.CSV
            self.behavior.exportFileSelected(dlg.GetPath(), _format)
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupPreferencesDialog(self):
        """
        Open the preferences dialog. See L{PreferencesDialog}.
        """
        dlg = PreferencesDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.behavior.preferencesChanged()
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupSearchDialog(self):
        """
        Open the search dialog. See L{SearchDialog}.
        """
        dlg = SearchDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.behavior.filterClicked(dlg.getSearchQuery())
        else:
            self.behavior.cancelClicked()
        dlg.Destroy()
    
    def popupAboutDialog(self):
        """
        Open the about box. See L{AboutBox}.
        The content of this dialog is contained in L{utils.resourcemgr.ResourceManager.getAboutHTML}
        """
        dlg = HTMLDialog(self, "About BiBler", resMgr.getAboutHTML())
        dlg.ShowModal()
        dlg.Destroy()
        return True
    
    def popupUserManualWindow(self):
        """
        Open the user manual. See L{UserManualWindow}.
        The content of this window is contained in L{utils.resourcemgr.ResourceManager.getUserManualHTML}
        """
        win = HTMLWindow(self, "User Manual", resMgr.getUserManualHTML())
        return win.Show(True)
    
    def popupConfirmExitDialog(self):
        """
        Prompt to confirm closing the window.
        """
        dlg = wx.MessageDialog(self, "Do you really want to exit?", "Confirm Exit",
                               wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            self.behavior.exit()
        else:
            self.behavior.cancelClicked()
    
    def popupPendingChangesOnExitDialog(self):
        """
        Prompt to ask if current bibliography must be saved before exiting.
        """
        dlg = wx.MessageDialog(self, "Do you want to save changes before exiting?", "Pending Changes",
                               wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.behavior.saveClicked(settings.ExportFormat.BIBTEX)
        else:
            self.behavior.forceExitClicked()
    
    def popupErrorMessage(self, msg):
        """
        Display an error message.
        """
        dlg = wx.MessageDialog(self, msg, "Error", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    
    def openURL(self, url):
        """
        Open a URL in a web browser. Note that local files can be open to.
        """
        return webbrowser.open(url, new=2)