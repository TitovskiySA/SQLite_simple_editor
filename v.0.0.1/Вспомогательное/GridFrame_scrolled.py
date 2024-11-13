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

        Sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 6, vgap = 6)
        Sizer.AddGrowableCol(0, 0)
        Sizer.AddGrowableRow(0, 1)
        Sizer.AddGrowableRow(1, 10)
        Sizer.AddGrowableRow(2, 1)

        self.panel1 = ButtonPanel(self)
        self.panel2 = GridPanel(self, data, rlabels, clabels)
        self.panel3 = ButtonPanel(self)
        self.SetMinSize((400, 400))

        Sizer.Add(self.panel1, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel2, -1, wx.EXPAND | wx.ALL, 0)
        Sizer.Add(self.panel3, -1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(Sizer)
        self.Fit()
        self.Show(True)

    def OnNew(self):
        self.panel2.OnNew()

    def OnDel(self):
        self.panel2.OnDel()
        
    def OnSave(self):
        self.panel2.OnSave()

#----------------------
#----------------------
#----------------------
#----------------------
class ButtonPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
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

        SaveBtn = wx.Button(self, wx.ID_ANY, "Save")
        Sizer.Add(SaveBtn, -1, wx.ALIGN_CENTRE|wx.ALL, 4)
        SaveBtn.Bind(wx.EVT_BUTTON, self.OnSave)

        self.SetSizer(Sizer)
        self.Fit()

    def OnNew(self, evt):
        print("Add row")
        self.parent.OnNew()

    def OnDel(self, evt):
        print("Del row")
        self.parent.OnDel()
        
    def OnSave(self, evt):
        print("Saving")
        self.parent.OnSave()
        
#----------------------
#----------------------
#----------------------
#----------------------
class GridPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, data, rlabels, clabels):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.SetupScrolling()
        
        Sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.grid = SimpleGrid(self, data, rlabels, clabels)
        Sizer.Add(self.grid, -1, wx.EXPAND | wx.ALL, 0)
        
        self.SetSizer(Sizer)
        #self.SetMinSize((400, 400))
        self.Fit()

    def OnNew(self):
        print("Add row command")
        self.grid.AppendRows(1, True)
        #self.grid.MakeCellVisible(row = self.grid.GetNumberRows(), col = 0)
        self.grid.Scroll(1000, 1000)
        #self.Refresh()

    def OnDel(self):
        print("Del row command")
        selected = self.grid.GetSelectedRows()
        print(str(selected))
        if selected != []:
            self.grid.DeleteRows(pos = selected[0], numRows = len(selected))

    def OnSave(self):
        print("Saving command")
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
        
        
        self.CreateGrid(len(data), len(data[0]))
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        for col in range (0, len(data[0])):
            self.AutoSizeColumn(col, True)
            self.SetColLabelValue(col, data[0][col])
            for row in range (0, len(data)):
                self.SetCellValue(row, col, data[row][col])

        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetSelectionBackground("gray")             
        
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

    

    
        
data = ("a", "b", "c", "d", "e", "f", "g", "h")
Data = [data for i in range (0, 20)]
RLabels = ("11", "12", "13", "14", "15", "16")
CLabels = ("First", "Second", "Third")
              
              
app = wx.App()
frame = GridFrame(None, Data, RLabels, CLabels)
app.MainLoop()
