import wx

from Constants import Constants


class ListItemPanel(wx.Panel):
    """
    Custom panel for word list items.
    """

    def __init__(self, *args, **kw):
        """
        Constructor for the list item panel.
        """
        super().__init__(*args, **kw)
        self._h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self._check_box = wx.CheckBox(self, -1)
        self._word = wx.StaticText(self, -1, 'test')
        self._count = wx.StaticText(self, -1, '100')

        self._h_sizer.Add(self._check_box, 0, wx.ALL, Constants.default_border)
        self._h_sizer.Add(self._word, 0, wx.TOP | wx.BOTTOM, Constants.default_border)
        self._h_sizer.Add(self._count, 0, wx.TOP | wx.BOTTOM, Constants.default_border)

        self._v_sizer.Add(self._h_sizer, 1, wx.EXPAND)

        self._v_sizer.Add(wx.StaticLine(self, -1, size=wx.Size(Constants.word_list_width, -1)), 0)

        self._h_sizer.SetMinSize(wx.Size(Constants.word_list_width - 10, -1))
        self.SetSizer(self._v_sizer)

        self._h_sizer.Layout()