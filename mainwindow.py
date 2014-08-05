#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Project: Quark Note Taker
File: mainwindow.py
Author: Leonardo Banderali
Created: August 3, 2014
Last Modified: August 3, 2014

Description:
    This file contains the class wich defines the main application window for Quark.


Copyright (C) 2014 Leonardo Banderali

License:

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""


#~import modules~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#python modules
import sys
import os

#extra modules
import markdown

#Qt objects
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *

#Quark specific
import quarkExtra
from noteeditor import NoteEditor



#~main window setup~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MainWindow(QMainWindow):
    """The main window class contains all the components of the app"""

    def __init__(self):
        super(MainWindow, self).__init__()

        #setup the main window menu
        self.mainToolBar = self.addToolBar("Main Toolbar")
        self.mainToolBar.setMovable(False)
        self.menu = {"File" : self.menuBar().addMenu("File")}
        self.menu["View"] = self.menuBar().addMenu("View")

        self.action = {"New": self.menu["File"].addAction("New")}
        self.action["Open"] = self.menu["File"].addAction("Open")
        self.action["Open"].setShortcut( QKeySequence.Open )
        self.action["Save"] = self.menu["File"].addAction("Save")
        self.action["Save As"] = self.menu["File"].addAction("Save As")
        self.action["Save Copy As"] = self.menu["File"].addAction("Save Copy As")
        self.menu["File"].addSeparator()
        self.action["Preview"] = self.menu["File"].addAction("Preview")

        self.actionGroup = {"display mode": QActionGroup(self) }
        self.action["View Mode"] = self.actionGroup["display mode"].addAction("View Mode")
        self.action["View Mode"].setCheckable(True)
        self.menu["View"].addAction( self.action["View Mode"] )
        self.action["Edit Mode"] = self.actionGroup["display mode"].addAction("Edit Mode")
        self.action["Edit Mode"].setCheckable(True)
        self.menu["View"].addAction( self.action["Edit Mode"] )
        self.action["Edit/View Mode"] = self.actionGroup["display mode"].addAction("Edit/View Mode")
        self.action["Edit/View Mode"].setCheckable(True)
        self.action["Edit/View Mode"].setChecked(True)
        self.menu["View"].addAction( self.action["Edit/View Mode"] )

        self.menu["View"].addSeparator()
        self.action["Note Manager"] = self.menu["View"].addAction("Note Manager")
        self.action["Note Manager"].setCheckable(True)
        self.action["Note Manager"].setChecked(False)

        #setup layout
        self.centralWidget = QSplitter(self)
        self.centralWidget.setOrientation(Qt.Horizontal)
        self.centralWidget.setChildrenCollapsible(False)
        self.setCentralWidget(self.centralWidget)

        self.noteManager = QTreeView(self.centralWidget)
        self.noteManager.setVisible(False)
        self.centralWidget.addWidget(self.noteManager)

        self.editingArea = QSplitter(self.centralWidget)
        #self.editingArea.setOrientation(Qt.Vertical)
        self.editingArea.setOrientation(Qt.Horizontal)
        self.editingArea.setChildrenCollapsible(False)
        self.centralWidget.addWidget(self.editingArea)

        self.noteEditor = NoteEditor(self.editingArea)

        #outputFile = open("out.html", "w")
        #outputFile.write(htmlDoc)
        #outputFile.close()

        self.notePreview = QWebView(self.editingArea)
        #self.notePreview.setHtml( htmlDoc,  QUrl("file://" + os.getcwd() + "/") )

        self.editingArea.addWidget(self.noteEditor)
        self.editingArea.addWidget(self.notePreview)

        #connect signals to slots
        self.action["Note Manager"].toggled.connect(self.noteManager.setVisible)
        self.actionGroup["display mode"].triggered.connect(self.changeLayoutOnAction)
        self.noteEditor.textChanged.connect(self.updatePreview)
        self.action["Open"].triggered.connect(self.openFileAction)


    def changeLayoutOnAction(self, action):
        """Changes the layout of the editing area (editor + preview window) based on the 'view' menu action triggered."""

        if action == self.action["View Mode"] :         #if the user choses to only display the note preview
            self.noteEditor.setVisible(False)
            self.notePreview.setVisible(True)

        elif action == self.action["Edit Mode"] :       #if the user choses to only display the note editor
            self.noteEditor.setVisible(True)
            self.notePreview.setVisible(False)

        elif action == self.action["Edit/View Mode"] :  #if the user choses to display both the note editor and note preview
            self.noteEditor.setVisible(True)
            self.notePreview.setVisible(True)


    def mdNoteToHtml(self, noteMarkdown):
        """Converts note text/markdown to an html document"""

        #create markdown parser
        parser = markdown.Markdown(['extra', 'toc', 'sane_lists'])

        #create an html document using the start (top/head) HTML template
        htmlFile = open(quarkExtra.config["start_html_template_file"] , "r")
        htmlDoc = htmlFile.read()
        htmlFile.close()

        #convert markdown note to html and append the result to the HTML document
        htmlDoc = htmlDoc + parser.convert(noteMarkdown)

        #append the end (bottom/foot) template to the HTML document
        htmlFile = open(quarkExtra.config["end_html_template_file"], "r")
        htmlDoc = htmlDoc + htmlFile.read()
        htmlFile.close()

        return htmlDoc

    def updatePreview(self):
        htmlDocument = self.mdNoteToHtml( self.noteEditor.toPlainText() )
        self.notePreview.setHtml(htmlDocument,  QUrl("file://" + os.getcwd() + "/" + quarkExtra.config["start_html_template_file"]) )

    def openFileAction(self):
        """Open an existing file by getting its path from a dialog."""

        searchPath = os.path.abspath(quarkExtra.config["notes_dir"])                #get the search directory
        filePath = QFileDialog.getOpenFileName(self, "Quark: Open File", searchPath)#get the file path from the user (note: 'filePath' is a tuple)
        if filePath[0] != "":                                                       #if the user did not hit the 'cancel' button
            self.noteEditor.openFileRequest(filePath[0])                                #open the file in the editor
