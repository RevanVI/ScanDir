import wx
import scan_dir

class Scan_UI(wx.Frame):

    def __init__(self, parent, title, dir_scanner):
        super(Scan_UI, self).__init__(parent, title=title) 
        self.scanner = dir_scanner
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(3, 3)

        path_text = wx.StaticText(panel, label="Path:")
        sizer.Add(path_text, pos=(0, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.path_tc = wx.TextCtrl(panel)
        sizer.Add(self.path_tc, pos=(0, 1), span=(1, 1),
            flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=5)
        
        self.browse_path_button = wx.Button(panel, id=wx.ID_ANY, label = "...")
        self.browse_path_button.Bind(wx.EVT_BUTTON, self.OnBrowseButtonClicked)
        sizer.Add(self.browse_path_button, pos = (0, 2), flag=wx.ALIGN_LEFT| wx.LEFT|wx.RIGHT|wx.TOP, border=5)

        # create parameters box
        parameters_sbox = wx.StaticBox(panel, id=wx.ID_ANY, label="Parameters:")
        sbox_static_sizer = wx.StaticBoxSizer(parameters_sbox, wx.VERTICAL)

        self.no_files_cbox = wx.CheckBox(panel, id=wx.ID_ANY, label="Ignore file in output")
        sbox_static_sizer.Add(self.no_files_cbox, flag = wx.LEFT | wx.TOP, border = 5)

        self.no_zero_dir_cbox = wx.CheckBox(panel, id=wx.ID_ANY, label="Ignore empty dirs in output")
        sbox_static_sizer.Add(self.no_zero_dir_cbox, flag = wx.LEFT | wx.TOP, border = 5)

        self.no_txt_cbox = wx.CheckBox(panel, id=wx.ID_ANY, label = "Do not save result to TXT file")
        sbox_static_sizer.Add(self.no_txt_cbox, flag = wx.LEFT | wx.TOP | wx.RIGHT, border = 5)

        self.no_csv_cbox = wx.CheckBox(panel, id=wx.ID_ANY, label = "Do not save result to CSV file")
        sbox_static_sizer.Add(self.no_csv_cbox, flag = wx.LEFT | wx.TOP | wx.RIGHT | wx.BOTTOM, border = 5)

        sizer.Add(sbox_static_sizer, pos=(1,0), span=(1,3), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        self.buttonScan = wx.Button(panel, label="Scan")
        self.buttonScan.Bind(wx.EVT_BUTTON, self.OnScanButtonClicked)
        sizer.Add(self.buttonScan, pos=(2, 2), flag= wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border = 10)

        #self.logs_tc = wx.TextCtrl(panel, id = wx.ID_ANY, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.ALIGN_LEFT)
        #self.logs = wx.LogTextCtrl(self.logs_tc)
        #sizer.Add(self.logs_tc, pos = (3, 0), span = (1, 3), flag = wx.EXPAND)

        sizer.AddGrowableCol(1)
        panel.SetSizer(sizer)

        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText("Idle")

        size = self.GetSize()
        self.SetMinSize(size)
        

    def OnBrowseButtonClicked(self, e):
        dlg = wx.DirDialog (None, "Choose scan directory", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        
        result = dlg.ShowModal()
        if (result == wx.ID_OK):
            self.path_tc.SetValue(dlg.GetPath())

 
    def OnScanButtonClicked(self, e):
        # collect options set
        args = {'dir_path': self.path_tc.GetValue(), 
            'ignore_files': self.no_files_cbox.IsChecked(), 
            'ignore_zero_size': self.no_zero_dir_cbox.IsChecked(), 
            'not_save_txt' : self.no_txt_cbox.IsChecked(),
            'not_save_csv' : self.no_csv_cbox.IsChecked()}

        print(f"Values: {args}")

        #validate path
        if scan_dir.validate_path(args["dir_path"]):
            self.sb.SetStatusText("Working")
            self.scanner.StartScan(args["dir_path"])
            self.scanner.Print_csv()
            self.sb.SetStatusText("Done")

            scan_result_info = self.scanner.GetBaseInfo()
            print(f"Scan path: {scan_result_info[0]}\n\
                Dir size: {scan_result_info[1]}\n\
                Files count: {scan_result_info[2]}\n\
                Dirs count: {scan_result_info[3]}\n")
        else:
            self.sb.SetStatusText("Failed: not real path")


def main():
    app = wx.App()
    scanner = scan_dir.DirScanner()
    ex = Scan_UI(None, title='Scan', dir_scanner=scanner)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()