'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This is the main BiBler module.
Execute this module from the command line to start the application.

@note: It assumes that the L{app} package has a L{statechart.BiBler_Statechart} class
and a L{UserInterface.UserInterface} class that implements L{gui.app_interface.IApplication}.

G{packagetree app, gui, utils}
'''

import wx
from gui.gui import MainWindow 
from gui.controller import Controller
from app.user_interface import UserInterface

def preload(controller):
    import testApplication.oracle as oracle
    for e in oracle.all_entries_all_fields:
        controller.addEntry()
        controller.data.currentEntryBibTeX = e.getBibTeX()
        controller.updateEntry()
    controller.data.entryList = controller.APP.getAllEntries()
    controller.displayEntries()

if __name__ == '__main__':
    app = wx.App(False)
    controller = Controller()
    controller.bindGUI(MainWindow(controller))
    controller.bindApp(UserInterface())
    #preload(controller)
    controller.start()
    app.MainLoop()