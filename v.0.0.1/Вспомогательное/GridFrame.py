import wx
import wx.grid
import wx.lib.scrolledpanel


#----------------------
#----------------------
#----------------------
#----------------------
class GridFrame(wx.Frame):
    def __init__(self, parent, data, rlabels, clabels):
        screenSize = wx.DisplaySize()
        wx.Frame.__init__(self, parent, -1, "Label")
        panel = GridPanel(self, data, rlabels, clabels)
        #self.SetSize((800, 800))
        self.Fit()
        self.Show(True)
        
        
#----------------------
#----------------------
#----------------------
#----------------------
#class GridPanel(wx.Panel):
class GridPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, data, rlabels, clabels):
        #wx.Panel.__init__(self, parent)
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.SetupScrolling()
        
        #self.scroll = wx.ScrolledWindow(self, -1)
        #self.scroll.SetScrollbars(1, 1, 600, 400)
        #self.scroll.FitInside()
        #self.Sizer = wx.BoxSizer()
        
        #self.Sizer = wx.FlexGridSizer(rows = 1, cols = 2, hgap = 6, vgap = 6)
        #self.Sizer.AddGrowableCol(1, 1)
        #elf.Sizer.AddGrowableRow(0, 1)
        self.Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)

        self.grid = SimpleGrid(self, data, rlabels, clabels)
        

        SemiSizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        #SemiSizer.AddGrowableRow(0, 0)
        SemiSizer.AddGrowableCol(0, 0)
        for rows in range (0, 3):
            SemiSizer.AddGrowableRow(rows, 1)

        NewBtn = wx.Button(self, wx.ID_ANY, "   +   ")
        NewBtn.Bind(wx.EVT_BUTTON, self.OnNew)
        SemiSizer.Add(NewBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)

        DelBtn = wx.Button(self, wx.ID_ANY, "   -   ")
        DelBtn.Bind(wx.EVT_BUTTON, self.OnDel)
        SemiSizer.Add(DelBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)

        SaveBtn = wx.Button(self, wx.ID_ANY, "Save")
        SemiSizer.Add(SaveBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)
        SaveBtn.Bind(wx.EVT_BUTTON, self.OnSave)

        #self.Sizer.Add(SemiSizer, -1, wx.EXPAND|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 4)

        
        #self.Sizer.Add(self.grid, -1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 4)
        self.Sizer.Add(self.grid, -1, wx.EXPAND|wx.ALL, 4)
        self.Sizer.Add(SemiSizer, -1, wx.EXPAND|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 4)
        
        self.SetSizer(self.Sizer)
        self.SetMinSize((800, 800))
        self.Fit()

    def OnNew(self, evt):
        print("Add row")
        self.grid.AppendRows(1, True)
        #self.grid.MakeCellVisible(row = self.grid.GetNumberRows(), col = 0)
        self.grid.Scroll(1000, 1000)
        #self.Refresh()

    def OnDel(self, evt):
        print("Del row")
        selected = self.grid.GetSelectedRows()
        print(str(selected))
        for part in selected:
            self.grid.DeleteRows(pos = part, numRows = 1)
        

    def OnSave(self, evt):
        print("Saving")
        newList = self.grid.GetValues()
        print(str(newList))
#----------------------
#----------------------
#----------------------
#----------------------
class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent, data, rlabels, clabels):
        wx.grid.Grid.__init__(self, parent, -1)
        self.data = data
        #self.tableBase = MyTable(data, rlabels, clabels)
        #self.tableBase = MyTable(data, collabels = clabels)
        #self.SetTable(self.tableBase)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.CreateGrid(len(data), len(data[0]))

        for rows in range (0, len(data)):
            for cols in range (0, len(data[0])):
                self.SetCellValue(rows, cols, data[rows][cols])
                
        
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnDClick)

    def OnLeftClick(self, evt):
        print("Left Clicked")
        evt.Skip()

    def OnDClick(self, evt):
        print("Double Clicked")

    def GetValues(self):
        temp = []
        for row in range (0, self.GetNumberRows()):
            temp.append([])
            for col in range (0, self.GetNumberCols()):
                temp[row].append(self.GetCellValue(row, col))
        return temp
                

#----------------------
#----------------------
#----------------------
#----------------------
class MyTable(wx.grid.GridTableBase):
    def __init__(self, data, rowlabels = None, collabels = None):
        wx.grid.GridTableBase.__init__(self)
        self.data = data
        if rowlabels == None:
            rowlabels = []
            first = 1
            for w in range(0, len(data)):
                rowlabels.append(str(first))
                first += 1
            rowlabels = tuple(rowlabels)
        self.rowLabels = rowlabels
        self.colLabels = collabels

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]
        else:
            return None

    def GetRowLabelValue(self, row):
        if self.rowLabels:
            return self.rowLabels[row]
        else:
            return None

    def IsEmptySell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        self.data[row][col] = value
        print("refreshed " + str(value) + " \nnow data = " + str(self.data))

    

    
        

Data = (
    ("a", "b"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"),
    ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"),
    ("a", "b"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"),
    ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"),
    ("a", "b"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"),
    ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"), ("j", "k"), ("c", "d"), ("e", "f"), ("g", "h"))
RLabels = ("11", "12", "13", "14", "15", "16")
CLabels = ("First", "Second", "Third")
              
              
app = wx.App()
frame = GridFrame(None, Data, RLabels, CLabels)
app.MainLoop()
