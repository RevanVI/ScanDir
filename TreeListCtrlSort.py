import wx
import wx.dataview



class TreeListCtrlSort(wx.dataview.TreeListCtrl):
    def __init__(self, *args, **kw):
        super(wx.dataview.TreeListCtrl, self).__init__(*args, **kw)
        self.ComparatorDict = {} 
        self.DefaultComparator = None
        self.Bind(wx.dataview.EVT_DATAVIEW_COLUMN_HEADER_CLICK, self.OnColumnHeaderClick)

    def __init__(self):
        super(wx.dataview.TreeListCtrl, self).__init__()
        self.ComparatorDict = {} 
        self.DefaultComparator = None
        self.Bind(wx.dataview.EVT_DATAVIEW_COLUMN_HEADER_CLICK, self.OnColumnHeaderClick)

    def __init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.dataview.TL_DEFAULT_STYLE, name=wx.dataview.TreeListCtrlNameStr):
        super(wx.dataview.TreeListCtrl, self).__init__(parent, id, pos, size, style, name)
        self.ComparatorDict = {} 
        self.DefaultComparator = None
        self.Bind(wx.dataview.EVT_DATAVIEW_COLUMN_HEADER_CLICK, self.OnColumnHeaderClick)


    def SetDefaultComparator(self, comparator = None):
        print("SetDefaultComparator")
        if isinstance(comparator, wx.dataview.TreeListItemComparator) or comparator is None:
            self.DefaultComparator = comparator
        else:
            raise TypeError()


    def SetColumnComparator(self, column, comparator = None):
        if column < 0 or column >= self.ColumnCount:
            raise IndexError()
        
        if not (isinstance(comparator, wx.dataview.TreeListItemComparator) or comparator is None):
            raise TypeError()
        
        self.ComparatorDict[column] = comparator
        

    def OnColumnHeaderClick(self, e):
        col = e.GetColumn()

        comparator = None
        try:
            comparator = self.ComparatorDict[col]
        except KeyError:
            comparator = self.DefaultComparator
        
        self.SetItemComparator(comparator)
        e.Skip()


    def DeleteColumn(self, col):
        isSorted, currentSortColumn, sortOrder = self.GetSortColumn()
        if isSorted and currentSortColumn in self.ComparatorDict:
            self.SetItemComparator(self.DefaultComparator)
            del self.ComparatorDict[currentSortColumn]

        return super().DeleteColumn(col)
    

    def ClearColumns(self):
        isSorted, currentSortColumn, sortOrder = self.GetSortColumn()
        if isSorted and currentSortColumn in self.ComparatorDict:
            self.SetItemComparator(self.DefaultComparator)
            del self.ComparatorDict
            self.ComparatorDict = {}

        return super().ClearColumns()


class NumericTreeListItemComparator(wx.dataview.TreeListItemComparator):
    def __init__(self):
        super(wx.dataview.TreeListItemComparator, self).__init__()

    def Compare(self, treelist, column, first, second):
        val_first = float(treelist.GetItemText(first, column))
        val_second = float(treelist.GetItemText(second, column))

        result = 0
        if val_first > val_second:
            result = 1
        elif val_first < val_second:
            result = -1

        return result