import wx
import wx.dataview
import scan_dir
import os
import TreeListCtrlSort


# todo
# icons
# context meu on tree items (show in explorer)
# last 10 scan directories




class Scan_UI(wx.Frame):
    class TreeCtrlConstants:
        NAME = 0
        SIZE = 1
        PERCENT = 2
        ITEMS = 3
        FILES = 4
        DIRS = 5


    def __init__(self, parent, title, dir_scanner):
        super(Scan_UI, self).__init__(parent, title=title)

        self.scanner = dir_scanner
        self.InitUI()


    # initial UI setup 
    def InitUI(self):
        self.InitMenuBar()
        self.InitStatusBar()
        self.InitToolBar()
        self.InitTreeCtrl()

        vboxsizer = wx.BoxSizer(wx.VERTICAL)
        vboxsizer.Add(self.toolbar1, proportion = 0, flag = wx.EXPAND)
        vboxsizer.Add(self.treeCtrl, proportion = 1, flag = wx.EXPAND)
        
        self.SetSizer(vboxsizer)
        size = self.GetSize()
        self.SetMinSize(size)

        
    def InitMenuBar(self):
        filemenu= wx.Menu()
        menuitem = filemenu.Append(wx.ID_ANY, "Save as &TXT")
        self.Bind(wx.EVT_MENU, self.OnSaveTxtButtonClicked, menuitem)
        menuitem = filemenu.Append(wx.ID_ANY, "Save as &CSV")
        self.Bind(wx.EVT_MENU, self.OnSaveCsvButtonClicked, menuitem)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, "E&xit","Close program")
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

        settings_menu = wx.Menu()
        self.HideFilesMenuCheckItem = settings_menu.AppendCheckItem(wx.ID_ANY, "Hide &files", help = "Show\hide files in output")
        self.HideZeroMenuCheckItem = settings_menu.AppendCheckItem(wx.ID_ANY, "Hide &zero size items", help = "Show\hide items with zero size in output")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(settings_menu, "&Settings")
        self.SetMenuBar(menuBar)


    def InitStatusBar(self):
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText("Idle")


    def InitTreeCtrl(self):
        self.treeCtrl = TreeListCtrlSort.TreeListCtrlSort(self)
        self.treeCtrl.SetDefaultComparator(TreeListCtrlSort.NumericTreeListItemComparator())
        
        self.treeCtrl.AppendColumn("Item", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)
        self.treeCtrl.SetColumnComparator(0, None)
        self.treeCtrl.AppendColumn("Size", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)
        self.treeCtrl.AppendColumn("%", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)
        self.treeCtrl.AppendColumn("Items", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)
        self.treeCtrl.AppendColumn("Files", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)
        self.treeCtrl.AppendColumn("Dirs", flags = wx.COL_SORTABLE | wx.COL_RESIZABLE)


    def InitToolBar(self):
        self.toolbar1 = wx.ToolBar(self, wx.TB_HORIZONTAL | wx.TB_TEXT)
        self.toolbar1.AddSeparator()
        self.path_tc = wx.TextCtrl(self.toolbar1, size = (250, wx.DefaultSize[1]))
        self.toolbar1.AddControl(self.path_tc, label = "Path to scan")
        
        browse_tool = self.toolbar1.AddTool(wx.ID_ANY, "Browse", wx.Bitmap('folder.png'), shortHelp = "Browse")
        self.Bind(wx.EVT_TOOL, self.OnBrowseButtonClicked, browse_tool)
        self.toolbar1.AddSeparator()

        scan_tool = self.toolbar1.AddTool(wx.ID_ANY, "Scan", wx.Bitmap('search.png'), shortHelp = "Scan")
        self.Bind(wx.EVT_TOOL, self.OnScanButtonClicked, scan_tool)

        self.toolbar1.AddSeparator()
        self.toolbar1.Realize()


    # event processors
    def OnBrowseButtonClicked(self, e):
        dlg = wx.DirDialog (None, "Choose scan directory", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        
        result = dlg.ShowModal()
        if (result == wx.ID_OK):
            self.path_tc.SetValue(dlg.GetPath())

 
    def OnScanButtonClicked(self, e):
        # collect options set
        args = {'dir_path': self.path_tc.GetValue(), 
            'not_save_txt' : False,
            'not_save_csv' : False}

        if scan_dir.validate_path(args["dir_path"]) == False:
            self.sb.SetStatusText("Failed: not real path")
            return

        self.SetStatusText("Working")
        showFiles = not self.HideFilesMenuCheckItem.IsChecked()
        showZeroSizeItems = not self.HideZeroMenuCheckItem.IsChecked()

        self.scanner.StartScan(args['dir_path'])
        self.FillData(showFiles, showZeroSizeItems)
        self.SetStatusText("Done")


    def OnSaveTxtButtonClicked(self, e):
        dlg = wx.FileDialog(None, "Save result", defaultDir = f"{os.path.dirname(os.path.realpath(__file__))}", defaultFile = "",
                            wildcard = "TXT files|.txt", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return  

        # save the current contents in the file
        pathname = dlg.GetPath()
        try:
            self.scanner.SaveTxt(pathname)
        except IOError:
            self.SetStatusText(f"Cannot save current data in file {pathname}")


    def OnSaveCsvButtonClicked(self, e):
        dlg = wx.FileDialog(None, "Save result", defaultDir = f"{os.path.dirname(os.path.realpath(__file__))}", defaultFile = "",
                    wildcard = "CSV files|.csv", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return  

        # save the current contents in the file
        pathname = dlg.GetPath()
        try:
            self.scanner.SaveCsv(pathname)
        except IOError:
            self.SetStatusText(f"Cannot save current data in file {pathname}")


    def OnExit(self, e):
        self.Close(True)


    # help functions
    def FillData(self, showFiles = True, showZeroSizeItems = True):
        self.treeCtrl.DeleteAllItems()

        data_dict = self.scanner.GetDict()
        base_info = self.scanner.GetBaseInfo()
        root_item = self.treeCtrl.GetRootItem()
        
        # stack for traversing dict tree data
        # tuple (dict key, parent TreeCtrl item)
        stack = []
        stack.append((base_info[0], root_item))

        while len(stack) != 0:
            dict_key, parent_tree_item = stack.pop()
            dict_item = data_dict[dict_key]

            if showFiles == False and os.path.isfile(dict_key):
                continue
            if showZeroSizeItems == False and dict_item[scan_dir.Constants.SIZE] == 0:
                continue

            short_name = os.path.split(dict_key)[1]
            percent = dict_item[scan_dir.Constants.SIZE] / base_info[1] * 100.0

            # add item to treeCtrl
            current_tree_item = self.treeCtrl.AppendItem(parent_tree_item, short_name)
            self.treeCtrl.SetItemText(current_tree_item, col = self.TreeCtrlConstants.SIZE, text = str(dict_item[scan_dir.Constants.SIZE]))
            self.treeCtrl.SetItemText(current_tree_item, col = self.TreeCtrlConstants.PERCENT, text = f"{percent:.2f}")
            self.treeCtrl.SetItemText(current_tree_item, col = self.TreeCtrlConstants.ITEMS, text = str(dict_item[scan_dir.Constants.CHILD_DIRS_COUNT] + dict_item[scan_dir.Constants.CHILD_FILES_COUNT]))
            self.treeCtrl.SetItemText(current_tree_item, col = self.TreeCtrlConstants.DIRS, text = str(dict_item[scan_dir.Constants.CHILD_DIRS_COUNT]))
            self.treeCtrl.SetItemText(current_tree_item, col = self.TreeCtrlConstants.FILES, text = str(dict_item[scan_dir.Constants.CHILD_FILES_COUNT]))

            for subfile in data_dict[dict_key][scan_dir.Constants.CHILD_FILES][::-1]:
                stack.append((subfile, current_tree_item))
            for subdir in data_dict[dict_key][scan_dir.Constants.CHILD_DIRS][::-1]:
                stack.append((subdir, current_tree_item))


    def SetStatusText(self, text):
        self.sb.SetStatusText(text)


def main():
    app = wx.App()
    dir_scanner = scan_dir.DirScanner()
    ex = Scan_UI(None, title='Scan', dir_scanner=dir_scanner)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()