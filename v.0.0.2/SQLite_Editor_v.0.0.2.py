#!/usr/bin/env python
#-*- coding: utf-8 -*-


import sys
import os
import sqlite3
import wx
import wx.grid
import wx.lib.scrolledpanel
from pubsub import pub
import threading
from threading import Thread
import time
import datetime  
from datetime import datetime
import locale
import queue

#=============================================
#=============================================
#=============================================
#=============================================
def ExceptDecorator(func):
    def wrapper():
        ToLog("Start of " + func.__name__)
        try:
            func()
        except Exception as Err:
            ToLog("Error in " + func.__name__ + ", Error code = " + str(Err))
        else:
            ToLog(func.__name__ + " finished succesfully")
    return wrapper

#=============================================
#=============================================
#=============================================
#=============================================
def ArgsExceptDecorator(func):
    def wrapper(**kwargs):
        print("Start of " + func.__name__)
        try:
            func(**kwargs)
        except Exception as Err:
            print("Error in " + func.__name__ + ", Error code = " + str(Err))
        else:
            print(func.__name__ + " finished succesfully")
    return wrapper


#========================================================================================
# создание класса основного окна
class MainWindow(wx.Frame):
    # задаем конструктор
    def __init__(self, parent, DocDir):
        global MyDate
        
        super().__init__(
            parent,
            title = "SQLiteSimpleEditor v.0.0.1 " + MyDate)
        
        frameIcon = wx.Icon(os.getcwd() + "\\images\\SQLico.ico")
        self.SetIcon(frameIcon)

        #Creating thread for saving logs
        thr = LogThread()
        thr.setDaemon(True)
        thr.start()
        
        self.panel = MainPanel(self, DocDir, thr)
        #self.Bind(wx.EVT_SIZE, self.ChangeSize)

        #mysize = (585, 400)
        
        #panel = MainPanel(self)
        self.Layout()
        self.Fit()
        self.Center()
        #self.SetClientSize(mysize)
        self.Show(True)       
        
#=======================================
#=======================================
#=======================================
#=======================================
# panel
class MainPanel(wx.Panel):

    def __init__(self, parent, docdir, thr):
        wx.Panel.__init__(self, parent = parent)

        self.frame = parent
        self.DocDir = docdir
        self.thrLog = thr
        
        colback = "#dadada"
        colfront = "#e7e7e7"
        self.SetBackgroundColour(wx.Colour(colback))

        #CommonVbox = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        #CommonVbox.AddGrowableRow(0, 1)
        #CommonVbox.AddGrowableRow(1, 1)
        #CommonVbox.AddGrowableRow(2, 1)
        CommonVbox = wx.FlexGridSizer(rows = 2, cols = 1, hgap = 6, vgap = 6)
        CommonVbox.AddGrowableRow(0, 1)
        CommonVbox.AddGrowableRow(1, 1)
        CommonVbox.AddGrowableCol(0, 1)
        #-----------------------------------------------------'''
        # Menu
        self.menuBar = wx.MenuBar()   
        MenuFile = wx.Menu()
        self.menuBar.Append(MenuFile, "File")

        MenuAbout = wx.Menu()
        self.menuBar.Append(MenuAbout, "About")

        self.frame.SetMenuBar(self.menuBar)

        LoadMenu = MenuFile.Append(-1, "Open...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoad, LoadMenu)

        NewMenu = MenuFile.Append(-1, "Create...")
        self.frame.Bind(wx.EVT_MENU, self.OnNew, NewMenu)

        MenuFile.AppendSeparator()

        MenuExit = MenuFile.Append(-1,"Exit")
        self.frame.Bind(wx.EVT_MENU, self.OnClose, MenuExit)
 
        License = MenuAbout.Append(-1, "License")
        self.frame.Bind(wx.EVT_MENU, self.ShowLic, License)

        #-----------------------------------------------------------------
        LoadBtn = wx.Button(self, wx.ID_ANY, "Оpen file with SQLite")
        LoadBtn.Bind(wx.EVT_BUTTON, self.OnLoad)

        NewBtn = wx.Button(self, wx.ID_ANY, "Create file with SQLite")
        NewBtn.Bind(wx.EVT_BUTTON, self.OnNew)
        #ButSize = (300, 200)
        #LoadBtn.SetSize(ButSize)
        CommonVbox.Add(LoadBtn, -1, wx.EXPAND | wx.ALL, 4)
        CommonVbox.Add(NewBtn, -1, wx.EXPAND | wx.ALL, 4)
        #CommonVbox.SetMinSize(ButSize)

        self.SetSizer(CommonVbox)
        self.SetSize((300, 400))
        #self.Fit()

        #pub.subscribe(self.UpdateDisplay, "Update")

        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)

#=====================
    def OnClose(self, evt):
        print("Closed")
        evt.Skip()

#=====================
    def ShowLic(self, evt):
        ToLog ("Нажата кнопка лицензии")
        LICENSE = (
            "Данная программа является свободным программным обеспечением\n"+
            "Вы вправе распространять её и/или модифицировать в соответствии\n"+
            "с условиями версии 2 либо по Вашему выбору с условиями более\n"+
            "поздней версии Стандартной общественной лицензии GNU, \n"+
            "опубликованной Free Software Foundation.\n\n\n"+
            "Эта программа создана в надежде, что будет Вам полезной, однако\n"+
            "на неё нет НИКАКИХ гарантий, в том числе гарантии товарного\n"+
            "состояния при продаже и пригодности для использования в\n"+
            "конкретных целях.\n"+
            "Для получения более подробной информации ознакомьтесь со \n"+
            "Стандартной Общественной Лицензией GNU.\n\n"+
            "Данная программа написана на Python\n"
            #"Особая благодарность за помощь в создании Анкешеву А.Д.\n\n"+
            "Автор: Титовский С.А.")
        
        wx.MessageBox(LICENSE, "Лицензия", wx.OK)

#======================================================================
    def OnLoad(self, evt):
        self.DoLoad()

    def DoLoad(self):
        try:
            ToLog("Load command")
            
            if self.DocDir + "\\temp\\temp.sql" in os.listdir(self.DocDir + "\\temp"):
                os.remove(self.DocDir + "\\temp\\temp.sql")
                ToLog("Previous temp file removed")
                                                              
            DialogLoad = wx.FileDialog(
                self,
                "Load file",
                defaultDir = self.DocDir,
                #wildcard = "TXT files (*.txt)|*txt",
                style = wx.FD_OPEN)

            if DialogLoad.ShowModal() == wx.ID_CANCEL:
                ToLog("Cancel loading")
                return

            else:
                UserPath = DialogLoad.GetDirectory()
                #print("GetDir = ", DialogLoad.GetDirectory())
                #print("GetFilename = ", DialogLoad.GetFilename())
                self.File = UserPath + "\\" + DialogLoad.GetFilename()
            
            self.tempFile = self.DocDir + "\\temp\\temp.sql"
            CopyFile(self.File, self.tempFile)

        except Exception as Err:
            ToLog("Error  in DoLoad, Error code = " + str(Err))
            #raise Exception
        
        else:
            ToLog("DoLoad function successed")
            self.ReadTables(self.tempFile)

#======================================================================
    def ReadTables(self, file):
        try:
            conn = sqlite3.connect(file)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            tables = [table[0] for table in cursor.fetchall()]

        except Exception as Err:
            ToLog("Error in ReadTables from file " + str(file) + ", Error code = " + str(Err))
            wx.MessageBox("Error in ReadTables from file " + str(file) + ", Error code = " + str(Err), " ", wx.OK)
            #raise Exception
            conn.close()
        else:
            if len(tables) > 0:
                ToLog("Found several tables in file " + str(file) + ", tables = " + str(tables))
                self.AskTable(conn, file, tables)
            elif len(tables) == 0:
                ToLog("No tables found in file " + str(file))
                wx.MessageBox("No tables found in file " + str(file), " ", wx.OK)
            #else:
            #    ToLog("Found one table in file " + str(file))
            #    self.ReadTableData(conn, tables[0])

#======================================================================
    def AskTable(self, conn, file, tables): 
        try:
            dlg = AskTableDlg(self, tables = tables, file = self.File)
            self.answer = None
            dlg.ShowModal()
            #print("answer = " + str(self.answer))
            if self.answer == "ok":
                #print(str(dlg.Value[0].GetSelection()))
                table = tables[dlg.Value[0].GetSelection()]
                ToLog("AskTable Choosed " + str(dlg.Value[0].GetStringSelection()))
                self.ReadTableData(conn, table)

            elif self.answer == "new":
                ToLog("New table pressed")
                ToLog("!!!!!!!!!!!!" + str(self.File) + ", " + str(self.tempFile))
                NewGridFrame(parent = self, file = self.File, tempfile = self.tempFile)
            else:
                ToLog("Cancel button pressed im AskTable")
                conn.close()
                return
        except Exception as Err:
            ToLog("Error in AskTable, Error code = " + str(Err))
            conn.close()
            #raise Exception

#======================================================================
    def ReadTableData(self, conn, table):
        try:
            #find labels and type of data
            LabelTypes = []
            cursor = conn.execute("SELECT name, type FROM pragma_table_info('" + table + "')")
            LabelTypes = [[row[0], row[1]] for row in cursor]
            #print("LabelTypes = " + str(LabelTypes))
            
            #read data from table
            cursor = conn.execute("SELECT * from " + table)
            Data = [row for row in cursor]
            #for row in Data:
            #    print(str(row))

        except Exception as Err:
            ToLog("Error in ReadTableData, Error code = " + str(Err))
            conn.close()

        else:
            ToLog("ReadTableData successed, opening GridFrame")
            conn.close()
            try:
                self.GridWindow = GridFrame(
                    parent = self, label = "Data of table " + table,
                    labels = LabelTypes, data = Data, file = self.File,
                    tempfile = self.tempFile, table = table)
            except Exception as Err:
                ToLog("Error opening GrigFrame for " + table + "in " + self.File + ", Error code = " + str(Err))
                #raise Exception
            else:
                ToLog("Grid frame for " + table + " in " + self.File + " opened succesfully")


    def OnNew(self, evt):
        self.DoNew()

    def DoNew(self):
        #print("OnNew")
        try:
            NewGridFrame(parent = self)
        except Exception as Err:
            ToLog("Error in DoNew SQLite, Error code = " + str(Err))
            #raise Exception
        else:
            ToLog("Successed DoNew SQLite")

#----------------------
#----------------------
#----------------------
#----------------------
class GridFrame(wx.Frame):
    def __init__(self, parent, label, labels = False, data = False, file = False, tempfile = False, table = False):
        #print("Data = " + str(data))
        label = "Editing table in " + os.path.basename(file)
        
        wx.Frame.__init__(self, parent, -1, label)
        frameIcon = wx.Icon(os.getcwd() + "\\images\\SQLico.ico")
        self.SetIcon(frameIcon)
        self.tempfile = tempfile
        self.file = file
        if data == []:
            wx.MessageBox(file + " has Empty Table " + table)
            data = [["" for label in labels]]
        
        Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        Sizer.AddGrowableCol(0, 0)
        #Sizer.AddGrowableRow(0, 1)
        #Sizer.AddGrowableRow(1, 1)
        Sizer.AddGrowableRow(2, 10)

        panelhead = HeadPanel(self, file = file, table = table)
        self.panel1 = ButtonPanel(self)
        self.panel2 = GridPanel(self, labels, data, file, tempfile, table)
        self.SetMinSize((400, 400))

        Sizer.Add(panelhead, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel1, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel2, -1, wx.EXPAND | wx.ALL, 0)
        #Sizer.Add(self.panel3, -1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(Sizer)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Fit()
        self.Show(True)

    def OnClose(self, evt):
        self.SaveTemp()
        evt.Skip()

    def ExceptDecorator(func):
        def wrapper(self):
            ToLog("Start of " + func.__name__)
            try:
                func(self)
            except Exception as Err:
                ToLog("Error in " + func.__name__ + ", Error code = " + str(Err))
            else:
                ToLog(func.__name__ + " finished succesfully")
        return wrapper

    @ExceptDecorator
    def SaveTemp(self):
        CopyFile(self.tempfile, self.file)
        
    #@ExceptDecorator
    def OnNew(self):
        self.panel2.OnNew()
        
    #@ExceptDecorator
    def OnDel(self):
        self.panel2.OnDel()

    #@ExceptDecorator        
    def OnSave(self):
        self.panel2.OnSave()
#----------------------
#----------------------
#----------------------
#----------------------
class NewGridFrame(wx.Frame):
    def __init__(self, parent, file = False, tempfile = False, table = False):
        if file == False:
            label = "Creating table of new file"
        else:
            label = "Creating new table in " + os.path.basename(file)
        wx.Frame.__init__(self, parent, -1, label)
        frameIcon = wx.Icon(os.getcwd() + "\\images\\SQLico.ico")
        self.SetIcon(frameIcon)
        self.parent = parent
        self.tempfile = tempfile
        self.file = file
        
        Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        Sizer.AddGrowableCol(0, 0)
        #Sizer.AddGrowableRow(0, 1)
        #Sizer.AddGrowableRow(1, 1)
        Sizer.AddGrowableRow(2, 10)

        self.panelhead = HeadPanel(self, file = file, table = table)
        self.panel1 = ButtonPanel(self, newGrid = True)
        #self.panel2 = GridPanel(self, labels, data, file, tempfile, table)
        self.panel2 = GridPanel(self, labels = ["Column0", "Column1"], data = [["", ""]], file = False, tempfile = tempfile, table = False, newGrid = True)
        #self.panel3 = ButtonPanel(self)
        self.SetMinSize((400, 400))

        Sizer.Add(self.panelhead, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel1, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel2, -1, wx.EXPAND | wx.ALL, 0)
        #Sizer.Add(self.panel3, -1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(Sizer)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        pub.subscribe(self.UpdateDisplay, "UpdateNGrid")
        
        self.Fit()
        self.Show(True)

    def UpdateDisplay(self, message):
        ToLog("message in NGridFrame = " + str(message))
        if self.tempfile != False:
            ToLog("Saving")
            CopyFile(self.tempfile, self.file)
    
        self.Destroy()

    def OnClose(self, evt):
        evt.Skip()
   
    def OnNew(self):
        self.panel2.OnNew()
        
    def OnDel(self):
        self.panel2.OnDel()
       
    def OnSave(self):
        self.panel2.OnCreateTable()

    def AskNames(self):
        try:
            names = (self.panelhead.FileName.GetValue(), self.panelhead.TableName.GetValue())
            ToLog("Loadded names " + ", ".join(names))
            for name in names:
                if len(name.strip()) == 0:
                    wx.MessageBox("Check if you filled FileName and TableName above the grid")
                    return

            self.panel2.ReadRows(names)
        except Exception as Err:
            ToLog("Error in AskNames, Error code = " + str(Err))
            #raise Exception


#----------------------
#----------------------
#----------------------
#----------------------
class HeadPanel(wx.Panel):
    def __init__(self, parent, file = False, table = False):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.file = file
        self.table = table
        colback = "#dadada"
        colfront = "#e7e7e7"
        self.SetBackgroundColour(wx.Colour(colback))
        
        Sizer = wx.FlexGridSizer(rows = 2, cols = 3, hgap = 6, vgap = 6)
        Sizer.AddGrowableRow(0, 0)
        Sizer.AddGrowableRow(1, 0)
        Sizer.AddGrowableCol(1, 0)
        #for cols in range (0, 3):
        #    Sizer.AddGrowableCol(cols, 0)

        FileText = wx.TextCtrl(
            self, wx.ID_ANY, "File = ", style = wx.TE_READONLY|wx.TE_CENTRE)
        FileText.SetBackgroundColour(wx.Colour(colfront))
        Sizer.Add(FileText, 5, wx.ALL|wx.EXPAND, 1)

        if file == False:
            ChFileBtn =  wx.Button(self, wx.ID_ANY, "Choose path")
            ChFileBtn.Bind(wx.EVT_BUTTON, self.OnChFile)
            self.FileName = wx.TextCtrl(
                self, wx.ID_ANY, "", style = wx.TE_READONLY|wx.TE_CENTRE)
        else:
            ChFileBtn = wx.StaticText(self, label = " ")
            self.FileName = wx.TextCtrl(
                self, wx.ID_ANY, file, style = wx.TE_READONLY|wx.TE_CENTRE)
            
        self.FileName.SetBackgroundColour(wx.Colour(colfront))
        Sizer.Add(self.FileName, 15, wx.ALL|wx.EXPAND, 1)
        Sizer.Add(ChFileBtn, 5, wx.ALL|wx.EXPAND, 1)

        TableText = wx.TextCtrl(
            self, wx.ID_ANY, "Table = ", style = wx.TE_READONLY|wx.TE_CENTRE)
        TableText.SetBackgroundColour(wx.Colour(colfront))
        Sizer.Add(TableText, 5, wx.ALL|wx.EXPAND, 1)

        if table == False:
            self.TableName = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_CENTRE)
        else:
            self.TableName = wx.TextCtrl(self, wx.ID_ANY, table, style = wx.TE_READONLY|wx.TE_CENTRE)
            self.TableName.SetBackgroundColour(wx.Colour(colfront))
            
            
        Sizer.Add(self.TableName, 15, wx.ALL|wx.EXPAND, 1)
        Sizer.Add(wx.StaticText(self, label = " "), 5, wx.ALL|wx.EXPAND, 1)

        self.SetSizer(Sizer)
        self.Fit()

    def OnChFile(self, evt):
        try:
            DialogSave = wx.FileDialog(
                self,
                "Create file fow saving",
                #defaultDir = self.DocDir + "\\profiles",
                #wildcard = "CFG files (*.cfg)|*cfg",
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

            if DialogSave.ShowModal() == wx.ID_CANCEL:
                return
            else:
                self.FileName.SetValue(DialogSave.GetDirectory() + "\\" + DialogSave.GetFilename())
        except Exception as Err:
            ToLog("Error in OnChFile, Error code = " + str(Err))
            #raise Exception
        else:
            ToLog("OnChFile successed, filepath = " + self.FileName.GetValue())
        
#----------------------
#----------------------
#----------------------
#----------------------
class ButtonPanel(wx.Panel):
    def __init__(self, parent, newGrid = False):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.newGrid = newGrid
        Sizer = wx.FlexGridSizer(rows = 1, cols = 3, hgap = 6, vgap = 6)
        Sizer.AddGrowableRow(0, 0)
        for cols in range (0, 3):
            Sizer.AddGrowableCol(cols, 0)

        NewBtn = wx.Button(self, wx.ID_ANY, "   +   ")
        NewBtn.Bind(wx.EVT_BUTTON, self.OnNew)
        Sizer.Add(NewBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)

        DelBtn = wx.Button(self, wx.ID_ANY, "   -   ")
        DelBtn.Bind(wx.EVT_BUTTON, self.OnDel)
        Sizer.Add(DelBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)

        if self.newGrid == False:
            SaveBtn = wx.Button(self, wx.ID_ANY, "Save")
            SaveBtn.Bind(wx.EVT_BUTTON, self.OnSave)
        else:
            SaveBtn = wx.Button(self, wx.ID_ANY, "Save Table to File")
            SaveBtn.Bind(wx.EVT_BUTTON, self.OnSaveTable)
            
        Sizer.Add(SaveBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)
        self.SetSizer(Sizer)
        self.Fit()

    def ExceptDecorator(func):
        def wrapper(self):
            ToLog("Start of " + func.__name__)
            try:
                func(self)
            except Exception as Err:
                ToLog("Error in " + func.__name__ + ", Error code = " + str(Err))
                #raise Exception
            else:
                ToLog(func.__name__ + " finished succesfully")
        return wrapper

    #@ExceptDecorator
    def OnNew(self, evt):
        #print("Add row")
        self.parent.OnNew()


    #@ExceptDecorator
    def OnDel(self, evt):
        #print("Del row")
        self.parent.OnDel()

    #@ExceptDecorator        
    def OnSave(self, evt):
        #print("Saving")
        self.parent.OnSave()

    def OnSaveTable(self, evt):
        self.SaveTable()

    @ExceptDecorator
    def SaveTable(self):
        names = self.parent.AskNames()
               
#----------------------
#----------------------
#----------------------
#----------------------
class GridPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, labels, data, file = False, tempfile = False, table = False, newGrid = False):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.parent = parent
        self.tempfile = tempfile
        self.file = file
        self.table = table
        self.labels = labels
        self.newGrid = newGrid
        self.Errors = []
        
        self.SetupScrolling()
        
        Sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.grid = SimpleGrid(self, labels, data, newGrid, tempfile)
        Sizer.Add(self.grid, -1, wx.EXPAND | wx.ALL, 0)

        self.SavingList = []
        self.SetSizer(Sizer)
        #self.SetMinSize((400, 400))
        self.Fit()

    def ExceptDecorator(func):
        def wrapper(self):
            ToLog("Start of " + func.__name__)
            try:
                func(self)
            except Exception as Err:
                ToLog("Error in " + func.__name__ + ", Error code = " + str(Err))
            else:
                ToLog(func.__name__ + " finished succesfully")
        return wrapper

    @ExceptDecorator
    def OnNew(self):
        if self.newGrid == False:
            self.grid.AppendRows(1, True)
            self.grid.Scroll(1000, 1000)
        else:
            self.grid.AppendCols(1, True)
            self.grid.Scroll(1000, 1000)
            self.grid.SetEditor()

    @ExceptDecorator
    def OnDel(self):
        if self.newGrid == False:
            selected = self.grid.GetSelectedRows()
            if selected != []:
                self.grid.DeleteRows(pos = selected[0], numRows = len(selected))
        else:
            selected = self.grid.GetSelectedCols()
            if selected != []:
                self.grid.DeleteCols(pos = selected[0], numCols = len(selected))

    @ExceptDecorator
    def OnSave(self):
        self.grid.OnSave(self.table, self.labels)
 
    def ReadRows(self, names):
        try:
            self.grid.ReadRows(names)
        except Exception as Err:
            ToLog("Error in ReadRows, Error code = " + str(Err))
            #raise Exception
        
#----------------------
#----------------------
#----------------------
#----------------------
class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent, labels, data, newGrid = False, tempfile = False):
        wx.grid.Grid.__init__(self, parent, -1)
        self.data = data
        self.parent = parent
        self.tempfile = tempfile
        if newGrid == False:
            self.types = [label[1] for label in labels]
            self.labels = [label[0] + "\n<" + label[1] + ">" for label in labels]
            self.data = data
        else:
            self.types = ["INT", "TEXT", "CHAR(50)", "REAL", "BLOB", "NULL"]
            self.BoolChoice = ["TRUE", "FALSE"]
            self.labels = ["A"]
            self.rowlabels = ["Name", "Type", "Primary Key", "NOT NULL"]
            self.data = [" " for label in self.rowlabels]
            
        self.newGrid = newGrid
        
        self.CreateGrid(len(self.data), len(self.labels))
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        for col in range (0, self.GetNumberCols()):
            #self.AutoSizeColumn(col, True)
            self.SetColLabelValue(col, self.labels[col])
            for row in range (0, self.GetNumberRows()):
                if str(self.data[row][col]) == "None":
                    continue
                self.SetCellValue(row, col, str(self.data[row][col]))
                if self.newGrid == True:
                    #ch_editor = wx.grid.GridCellChoiceEditor(["True", "False", "Something else"], True)
                    self.SetRowLabelValue(row, self.rowlabels[row])
                    #self.SetCellEditor(row, col, ch_editor)
                    if row == 1:
                        ch_editor = wx.grid.GridCellChoiceEditor(self.types, False)
                        self.SetCellEditor(row, col, ch_editor)
                        self.SetCellValue(row, col, "TEXT")
                    elif row > 1:
                        ch_editor = wx.grid.GridCellChoiceEditor(self.BoolChoice, False)
                        self.SetCellEditor(row, col, ch_editor)
                        self.SetCellValue(row, col, "FALSE")

        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetSelectionBackground("gray")             
        
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnDClick)
            

    def ExceptDecorator(func):
        def wrapper(self):
            ToLog("Start of " + func.__name__)
            try:
                func(self)
            except Exception as Err:
                ToLog("Error in " + func.__name__ + ", Error code = " + str(Err))
                #raise Exception
            else:
                ToLog(func.__name__ + " finished succesfully")
        return wrapper
        
    def OnLeftClick(self, evt):
        evt.Skip()

    def OnDClick(self, evt):
        evt.Skip()

    @ExceptDecorator
    def SetEditor(self):
        ch_editor = wx.grid.GridCellChoiceEditor(self.types, False)
        self.SetCellEditor(1, self.GetNumberCols() - 1, ch_editor)
        self.SetCellValue(1, self.GetNumberCols() - 1, "TEXT")
                   
        ch_editor = wx.grid.GridCellChoiceEditor(self.BoolChoice, False)
        self.SetCellEditor(2, self.GetNumberCols() - 1, ch_editor)
        self.SetCellValue(2, self.GetNumberCols() - 1, "FALSE")
        self.SetCellEditor(3, self.GetNumberCols() - 1, ch_editor)
        self.SetCellValue(3, self.GetNumberCols() - 1, "FALSE")

    def OnSave(self, table, labels):
        try:
            self.table = table
            self.tablelabels = labels
            self.GetValues()
        except Exception as Err:
            ToLog("Error in OnSave grid, Error code = " + str(Err))
            #raise Exception
        

    @ExceptDecorator
    def GetValues(self):
        temp = []
        temp2 = []
        for row in range (0, self.GetNumberRows()):
            temp.append([])
            temp2.append(row)
            for col in range (0, self.GetNumberCols()):
                self.SetCellBackgroundColour(row, col, wx.NullColour)
                if self.GetCellValue(row, col) == "":
                    temp[row].append("<NULLVALUE>")
                else:
                    temp[row].append(self.GetCellValue(row, col))
        self.SaveToSQL([temp2[:], temp[:]])
        self.Refresh()

    def SaveToSQL(self, data):
        try:
            self.Errors = []
            conn = sqlite3.connect(self.tempfile)
            conn.execute("delete from " + self.table)
            for i in range(0, len(data[0])):
                self.SaveRow(conn, data[0][i], data[1][i])
            conn.commit()
            conn.close()

        except Exception as Err:
            ToLog("Error in SaveToSQL, Error code = " + str(Err))

        else:
            if self.Errors == []:
                wx.MessageBox("Data saved succesfully", " ", wx.OK)
            else:
                wx.MessageBox("Some Errors found in rows coloured red", " ", wx.OK)
                


    def SaveRow(self, conn, rowNum, row):
        try:
            label = [label[0] for label in self.tablelabels]
            typeData = [label[1] for label in self.tablelabels]
            #print("label = " + ",".join(label))
            #print("data = " + ",".join(typeData))
            #print("row = " + ",".join(row))
            newRow = self.formatRow(row[:], typeData, label)
            #print("NewRow = " + str(newRow))
            if isinstance (newRow, str):             
                self.Errors.append("Error in row " + " | ".join(row))
                ToLog("Error in row " + " | ".join(row) + " reason = " + newRow)   
            else:
                ToLog("INSERT INTO " + self.table + " (" + ",".join(newRow[0]) + ") VALUES (" + ",".join(newRow[1]) + ")")
                conn.execute("INSERT INTO " + self.table + " (" + ",".join(newRow[0]) + ") VALUES (" + ",".join(newRow[1]) + ")")
        except Exception as Err:
            #raise Exception
            self.PaintError(rowNum, str(Err))
            self.Errors.append(str(Err))
        else:
            ToLog("inserted row " + str(newRow))

    def formatRow(self, row, typeData, label):
        try:
            FormattedRow = [[], []]
            for i in range (0, len(typeData)):
                if (
                    "CHAR" in typeData[i] or
                    "CLOB" in typeData[i] or
                    "TEXT" in typeData[i]):
                    row[i] = "'" + row[i] + "'"
            for i in range (0, len(typeData)):
                if row[i].find("<NULLVALUE>") != -1:
                    continue
                FormattedRow[0].append(label[i])
                FormattedRow[1].append(row[i])
        
        except Exception as Err:
            ToLog("Error  in formatRow, Error code = " + str(Err))
            #raise Exception
            return str(Err)
        else:
            ToLog("formatRow successfull, row = " + str(FormattedRow[:]))
            return FormattedRow[:]

    def PaintError(self, num, ErrCode):
        try:
            for col in range (0, self.GetNumberCols()):
                self.SetCellBackgroundColour(num, col, wx.RED)
            self.Refresh()
        except Exception as Err:
            ToLog("Error in PaintError, Error code = " + str(Err))
            #raise Exception
        else:
            ToLog("Painted row " + str(num) + " succesfully, Error = " + str(ErrCode))

    def ReadRows(self, names):
        try:
            ToLog("Start ReadRows in Grid with names " + ", ".join(names))
            TableData = []
            for cols in range (0, self.GetNumberCols()):
                TableData.append([])
                for rows in range (0, self.GetNumberRows()):
                    TableData[cols].append(self.GetCellValue(rows, cols))

            self.CheckTableData(names, TableData[:])

        except Exception as Err:
            ToLog("Error in ReadRows in Grid, Error code = " + str(Err))
            #raise Exception

    def CheckTableData(self, names, datas):
        try:
            ToLog("Start CheckTableData with names " + ", ".join(names))
            numPrimId = 0
            for col in datas:
                if col[0].strip() == "":
                    wx.MessageBox("In some Column Id name is empty. Please, check Id names.", " ", wx.OK)
                    ToLog("Some column Id in datas was empty, saving cancelled")
                    return
                if col[2] == "TRUE" and col[3] == "FALSE":
                    wx.MessageBox("NOT NULL field for PRIMARY KEY must be TRUE", " ", wx.OK)
                    ToLog("NOT NULL field for PRIMARY KEY must be TRUE, saving cancelled")
                    return
                if col[2] == "TRUE":
                    numPrimId = numPrimId + 1
                    col[2] = "PRIMARY KEY"
                else:
                    col[2] = ""
                if col[3] == "TRUE":
                    col[3] = "NOT NULL"
                else:
                    col[3] = ""

            if numPrimId != 1:
                wx.MessageBox("Choose ONE Primary Key field", " ", wx.OK)
                ToLog("Choose ONE Primary Key field")
                return

        except Exception as Err:
            ToLog("Error in CheckTableData, Error code = " + str(Err))
            #raise Exception
        else:
            self.SaveTableToSQL(names, datas)

    def SaveTableToSQL(self, names, data):
        try:
            ToLog("Start SaveTableToSQL with names " + " | ".join(names) + ",and datatypes " + str(data))
            temp = [" ".join(cols) for cols in data]
            #ToLog("tempSQL = " + str(temp))
            strToSQL = "CREATE TABLE IF NOT EXISTS " + names[1] + " (" + " ,".join(temp) + ");"
            ToLog("strToSQL = " + str(strToSQL))

            if self.tempfile == False:
                conn = sqlite3.connect(names[0])
            else:
                conn = sqlite3.connect(self.tempfile)
            conn.execute(strToSQL)

            wx.MessageBox("Table " + names[1] + " saved in " + names[0] + " succesfully")
            #cursor = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            #tables = [table[0] for table in cursor.fetchall()]
            #ToLog("Now tables are = " + " | ".join(tables))

            conn.commit()
            conn.close()

            #self.parent.parent.Destroy()

        except Exception as Err:
            ToLog("Error in SaveTableToSQL, Error code = " + str(Err))
            raise Exception

        else:
            wx.CallAfter(
                pub.sendMessage,
                "UpdateNGrid",
                message = "Done")

#=============================================
#=============================================
#=============================================
#=============================================
#Dialog of devices
class AskTableDlg(wx.Dialog):
    def __init__(
        self, parent, tables, label = "Choose Table from Database", file = "NULL file"):

        #wx.Dialog.__init__(self, None, -1, label, size = (300,300))
        wx.Dialog.__init__(self, parent, -1, label)
        self.parent = parent
        labels = [
            "Choose one or and new table to file \n" + os.path.basename(file)]

        posSText = [(10, 10)]
        for i in range (0, len(labels)):
            text = wx.StaticText(self, wx.ID_ANY, labels[i], pos = posSText[i])
            text.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        posText = [(10, 55)]
        self.Value = []
        for i in range(0, len(posText)):
            temp = wx.Choice(self, wx.ID_ANY, pos = posText[i], size = (260, 30), choices = tables)
            temp.SetSelection(0)
            temp.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
            self.Value.append(temp)

        NewButton = wx.Button(self, wx.ID_ANY, "Add new", pos = (20, 125), size = (100, 30))
        NewButton.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        NewButton.Bind(wx.EVT_BUTTON, self.OnNew)
        
        OKButton = wx.Button(self, wx.ID_ANY, "Select", pos = (160, 125), size = (100, 30))
        OKButton.SetDefault()
        OKButton.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        OKButton.Bind(wx.EVT_BUTTON, self.OnOk)
        
        self.SetClientSize((280, 180))
        self.Bind(wx.EVT_CLOSE, self.NoClose)

    def NoClose(self, evt):
        self.parent.answer = "cancel"
        self.Destroy()
        return

    def OnNew(self, evt):
        self.parent.answer = "new"
        self.Destroy()
        return

    def OnOk(self, evt):
        self.parent.answer = "ok"
        self.Destroy()
        return 
        
#=============================================
#=============================================
#=============================================
#=============================================
# scaling bitmaps
def ScaleBitmap(bitmap, size):
    image = bitmap.ConvertToImage()
    image = image.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
    return wx.Image(image).ConvertToBitmap()
#=============================================
#=============================================
#=============================================
#=============================================
def CopyFile(source, dist, buffer = 1024*1024):
    ToLog("CopyFile " + source + " to " + dist + " function started")
    with open(source, "rb") as SrcFile, open(dist, "wb") as DestFile:
        while True:
            copy_buffer = SrcFile.read(buffer)
            if not copy_buffer:
                break
            DestFile.write(copy_buffer)
    ToLog("CopyFile " + source + " to " + dist + " function finished")
#=============================================
#=============================================
#=============================================
#=============================================
# ClearOldLogs
@ExceptDecorator
def ClearLogs():    
    global LogDir
    while len(os.listdir(LogDir)) >= 10:
        if len(os.listdir(LogDir)) < 10:
                break
        try:
            os.remove(os.path.abspath(FindOldest(LogDir)))
            print("DELETING FILE " + str(FindOldest(LogDir)))
        except Exception as Err:
            ToLog("Old file with logs wasn't deleted, Error code = " + str(Err))
            #raise Exception
            break
#=============================================
#=============================================
#=============================================
#=============================================   
# DeleteOldest
def FindOldest(Dir):
    try:
        List = os.listdir(Dir)
        fullPath = [Dir + "/{0}".format(x) for x in List]
        oldestFile = min(fullPath, key = os.path.getctime)
        return oldestFile
    except Exception as Err:
        ToLog("Error of finding oldest file in dir, Error code = " + str(Err))
        #raise Exception
        return False
#=============================================
#=============================================
#=============================================
#=============================================
def FindMyDir(nameDir, subDirs = None):
    try:
        if "Documents" in os.listdir(os.path.expanduser("~")):
            DocDir = os.path.expanduser("~") + "\\Documents"
        else:
            os.mkdir(os.path.expanduser("~") + "\\Documents")
            DocDir = os.path.expanduser("~") + "\\Documents"
        if nameDir not in os.listdir(DocDir):
            os.mkdir(DocDir + "\\" + nameDir)
            ToLog(nameDir + "folder was Created")
        if isinstance (subDirs, list):
            for word in subDirs:
                if word not in os.listdir(DocDir + "\\" + nameDir):
                    os.mkdir(DocDir + "\\" + nameDir + "\\" + word)
                    ToLog(word + " folder was Created")
    except Exception as Err:
        ToLog("Error in FindMyDir, Error code = " + str(Err))  
        #raise Exception
        return os.path.expanduser("~") + "\\" + NameDir
    else:
        ToLog("FindMyDir finished succesfully")
        return DocDir + "\\" + nameDir

#=============================================
#=============================================
#=============================================
#=============================================
# Tolog - renew log
def ToLog(message, startThread = False):
    try:
        global LogQueue
        LogQueue.put(str(datetime.today())[10:19] + "  " + str(message) + "\n")
    except Exception as Err:
        print("Error in ToLog function, Error code = " + str(Err))
        
#=============================================
#=============================================
#=============================================
#=============================================
# Thread for saving logs
class LogThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop = False

    def run(self):
        global LogQueue
        ToLog("LogThread started!!!")
        self.writingQueue()
        ToLog("LogThread finished!!!")

    def writingQueue(self):
        global LogQueue, LogDir
        while True:
            try:
                if LogQueue.empty():
                    if self.stop == True:
                        print("LogThreadStopped")
                        break
                    time.sleep(1)
                    continue
                else:
                    with open(LogDir + "\\" + str(datetime.today())[0:10] + ".cfg", "a") as file:
                        while not LogQueue.empty():
                            mess = LogQueue.get_nowait()
                            file.write(mess)
                            print("Wrote to Log:\t" + mess)
                        file.close()
            except Exception as Err:
                print("Error writing to Logfile, Error code = " + str(Err))
                #raise Exception

#=============================================
#=============================================
#=============================================
#=============================================
# Определение локали!
locale.setlocale(locale.LC_ALL, "")

global LogDir, LogQueue, MyDate
LogQueue = queue.Queue()
MyDate = "18.03.2024"

ToLog("!" * 40)
ToLog("Application started")

DocDir = FindMyDir(nameDir = "SQLite_RedactorFiles", subDirs = ["logs", "temp"])
LogDir = DocDir + "\\Logs"
ClearLogs()

ex = wx.App()

MainWindow(parent = None, DocDir = DocDir)

ex.MainLoop()
