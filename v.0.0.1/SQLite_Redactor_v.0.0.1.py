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
            title = "SQLite_Redactor v.0.0.1 " + MyDate)
        
        #frameIcon = wx.Icon(os.getcwd() + "\\images\\icon_png.png")
        #self.SetIcon(frameIcon)

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
        self.menuBar.Append(MenuFile, "Файл")

        MenuAbout = wx.Menu()
        self.menuBar.Append(MenuAbout, "Справка")

        self.frame.SetMenuBar(self.menuBar)

        LoadMenu = MenuFile.Append(-1, "Открыть sqlite...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoad, LoadMenu)

        NewMenu = MenuFile.Append(-1, "Создать sqlite...")
        self.frame.Bind(wx.EVT_MENU, self.OnNew, NewMenu)

        MenuFile.AppendSeparator()

        MenuExit = MenuFile.Append(-1,"Выход")
        self.frame.Bind(wx.EVT_MENU, self.OnClose, MenuExit)
 
        License = MenuAbout.Append(-1, "Лицензия")
        self.frame.Bind(wx.EVT_MENU, self.ShowLic, License)

        #-----------------------------------------------------------------
        LoadBtn = wx.Button(self, wx.ID_ANY, "Открыть файл с базами данных SQLite")
        LoadBtn.Bind(wx.EVT_BUTTON, self.OnLoad)

        NewBtn = wx.Button(self, wx.ID_ANY, "Создать файл с базами данных SQLite")
        NewBtn.Bind(wx.EVT_BUTTON, self.OnNew)
        #ButSize = (300, 200)
        #LoadBtn.SetSize(ButSize)
        CommonVbox.Add(LoadBtn, -1, wx.EXPAND | wx.ALL, 4)
        CommonVbox.Add(NewBtn, -1, wx.EXPAND | wx.ALL, 4)
        #CommonVbox.SetMinSize(ButSize)

        self.SetSizer(CommonVbox)
        self.SetSize((300, 400))
        #self.Fit()

        pub.subscribe(self.UpdateDisplay, "Update")

        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)

#=====================
    def OnClose(self, evt):
        print("Closed")
        evt.Skip()

#=====================
    def ShowLic(self, evt):
        print("Lic here")

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
                "Загрузить файл SQLite",
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
            raise Exception
        
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
            conn.close()
        else:
            if len(tables) > 0:
                ToLog("Found several tables in file " + str(file))
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
            dlg = AskTableDlg(self, tables = tables, file = file)
            self.answer = None
            dlg.ShowModal()
            print("answer = " + str(self.answer))
            if self.answer == "ok":
                print(str(dlg.Value[0].GetSelection()))
                table = tables[dlg.Value[0].GetSelection()]
                ToLog("AskTable Choosed " + str(dlg.Value[0].GetStringSelection()))
                self.ReadTableData(conn, table)
REWRITE HERE FOR NEW table
            elif self.answer == "new":
                print("New table pressed")
                conn.close()
                return
            else:
                ToLog("Cancel button pressed im AskTable")
                conn.close()
                return
        except Exception as Err:
            ToLog("Error in AskTable, Error code = " + str(Err))
            conn.close()
            raise Exception


#======================================================================
    def ReadTableData(self, conn, table):
        try:
            #find labels and type of data
            LabelTypes = []
            cursor = conn.execute("SELECT name, type FROM pragma_table_info('" + table + "')")
            LabelTypes = [[row[0], row[1]] for row in cursor]
            print("LabelTypes = " + str(LabelTypes))
            
            #read data from table
            cursor = conn.execute("SELECT * from " + table)
            Data = [row for row in cursor]
            for row in Data:
                print(str(row))

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
        print("OnNew")
        try:
            self.GridWindow = NewGridFrame(
                parent = self, label = "New table SQLite")
        except Exception as Err:
            ToLog("Error in DoNew SQLite, Error code = " + str(Err))
            raise Exception
        else:
            ToLog("Successed DoNew SQLite")
        
#'''----------------------------------------------------------------------------------------'''

                
# Функция обновления окна прогресса
    def UpdateDisplay(self, message):
        ToLog("message in MainFrame = " + str(message))

#----------------------
#----------------------
#----------------------
#----------------------
class GridFrame(wx.Frame):
    def __init__(self, parent, label, labels = False, data = False, file = False, tempfile = False, table = False):
        print("Data = " + str(data))
        wx.Frame.__init__(self, parent, -1, label)
        self.tempfile = tempfile
        self.file = file
        if data == []:
            wx.MessageBox(file + " has Empty Table " + table)
            data = [["" for label in labels]]
        
        Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        Sizer.AddGrowableCol(0, 0)
        Sizer.AddGrowableRow(0, 1)
        Sizer.AddGrowableRow(1, 10)
        Sizer.AddGrowableRow(2, 1)

        self.panel1 = ButtonPanel(self)
        self.panel2 = GridPanel(self, labels, data, file, tempfile, table)
        #self.panel3 = ButtonPanel(self)
        self.SetMinSize((400, 400))

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
    def __init__(self, parent, label):
        wx.Frame.__init__(self, parent, -1, label)
        
        Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        Sizer.AddGrowableCol(0, 0)
        Sizer.AddGrowableRow(0, 1)
        Sizer.AddGrowableRow(1, 10)
        Sizer.AddGrowableRow(2, 1)

        self.panel1 = ButtonPanel(self, newGrid = True)
        #self.panel2 = GridPanel(self, labels, data, file, tempfile, table)
        self.panel2 = GridPanel(self, labels = ["Column0", "Column1"], data = [["", ""]], file = False, tempfile = False, table = False, newGrid = True)
        #self.panel3 = ButtonPanel(self)
        self.SetMinSize((400, 400))

        Sizer.Add(self.panel1, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel2, -1, wx.EXPAND | wx.ALL, 0)
        #Sizer.Add(self.panel3, -1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(Sizer)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Fit()
        self.Show(True)

    def OnClose(self, evt):
        #self.SaveTemp()
        evt.Skip()
   
    def OnNew(self):
        self.panel2.OnNew()
        
    def OnDel(self):
        self.panel2.OnDel()
       
    def OnSave(self):
        self.panel2.OnCreateTable()
        
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
            SaveBtn = wx.Button(self, wx.ID_ANY, "Column\nProperties")
            SaveBtn.Bind(wx.EVT_BUTTON, self.OnProperties)
            
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

    def OnProperties(self, evt):
        ToLog("Here ll be properties frame")
        
#----------------------
#----------------------
#----------------------
#----------------------
class GridPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, labels, data, file = False, tempfile = False, table = False, newGrid = False):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.tempfile = tempfile
        self.file = file
        self.table = table
        self.labels = labels
        self.newGrid = newGrid
        self.Errors = []
        
        self.SetupScrolling()
        
        Sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.grid = SimpleGrid(self, labels, data, newGrid)
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
        self.grid.GetValues()
        print("saved data = " + str(self.SavingList))
        self.SaveToSQL(self.SavingList[:])

    
    def SaveToSQL(self, data):
        try:
            self.Errors.clear()
            conn = sqlite3.connect(self.tempfile)
            conn.execute("delete from " + self.table)
            for i in range(0, len(data[0])):
                self.SaveRow(conn, data[0][i], data[1][i])
            conn.commit()
            conn.close()

        except Exception as Err:
            raise Exception

    def SaveRow(self, conn, rowNum, row):
        try:
            label = [label[0] for label in self.labels]
            typeData = [label[1] for label in self.labels]
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
            self.grid.PaintError(rowNum, str(Err))
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
            
    @ExceptDecorator
    def OnCreateTable(self):
        print("OnCreateTable")
            
        
#----------------------
#----------------------
#----------------------
#----------------------
class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent, labels, data, newGrid = False):
        wx.grid.Grid.__init__(self, parent, -1)
        self.data = data
        self.parent = parent
        if newGrid == False:
            self.types = [label[1] for label in labels]
            self.labels = [label[0] + "\n<" + label[1] + ">" for label in labels]
            self.data = data
        else:
            self.types = ["INT", "TEXT", "CHAR(50)", "REAL", "BLOB", "NULL"]
            self.BoolChoice = ["True", "False"]
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
                        ch_editor = wx.grid.GridCellChoiceEditor(self.types, True)
                        self.SetCellEditor(row, col, ch_editor)
                    elif row > 1:
                        ch_editor = wx.grid.GridCellChoiceEditor(self.BoolChoice, True)
                        self.SetCellEditor(row, col, ch_editor)

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
            else:
                ToLog(func.__name__ + " finished succesfully")
        return wrapper
        
    def OnLeftClick(self, evt):
        evt.Skip()
        #if self.newGrid == False:
        #    evt.Skip()
        #else:
        #   print("No action here")

    def OnDClick(self, evt):
        evt.Skip()
        
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
                #print("appending " + self.GetCellValue(row, col))
        #print(str(temp[:]))
        self.parent.SavingList = [temp2[:], temp[:]]
        self.Refresh()
        return
        #return temp[:]

    def PaintError(self, num, ErrCode):
        try:
            for col in range (0, self.GetNumberCols()):
                self.SetCellBackgroundColour(num, col, wx.RED)
            self.Refresh()
        except Exception as Err:
            ToLog("Error in PaintError, Error code = " + str(Err))
            raise Exception
        else:
            ToLog("Painted row " + str(num) + " succesfully, Error = " + str(ErrCode))


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
    ToLog("CopyFile " + source + " to " + dist + "function started")
    with open(source, "rb") as SrcFile, open(dist, "wb") as DestFile:
        while True:
            copy_buffer = SrcFile.read(buffer)
            if not copy_buffer:
                break
            DestFile.write(copy_buffer)
    ToLog("CopyFile " + source + " to " + dist + "function finished")
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




#@exceptDecorator
#def say_hello():
#    print("Привет!")

#@exceptDecorator2
#def devision(**kwargs):
#    default = {"a": 20, "b": 1}
#    for defname, value in default.items():
#        if defname not in kwargs:
#            print("default " + f"defname" + " = " + f"{value}")
#            kwargs[defname] = value
#    for name, value in kwargs.items():
#        print(f"{name}: {value}")
    #print(str(kwargs["a"]))
#    print(str(kwargs))
    
#    print("a/b = " + str(kwargs["a"]/kwargs["b"]))
#=============================================
#=============================================
#=============================================
#=============================================
# Определение локали!
locale.setlocale(locale.LC_ALL, "")

global LogDir, LogQueue, MyDate
LogQueue = queue.Queue()
MyDate = "13.03.2024"

ToLog("!" * 40)
ToLog("Application started")

DocDir = FindMyDir(nameDir = "SQLite_RedactorFiles", subDirs = ["logs", "temp"])
LogDir = DocDir + "\\Logs"
ClearLogs()

ex = wx.App()

MainWindow(parent = None, DocDir = DocDir)

ex.MainLoop()
