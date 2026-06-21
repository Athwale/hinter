import wx

from Constants import Constants, Strings


class PlainTextEditDialog(wx.Dialog):

    def __init__(self, parent, word_list: str):
        """
        Show a simple plain text editor with a file opened with the ability to save the file.
        Used for word lists.
        :param parent: Parent frame.
        :param word_list: Word list name
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_edit,
                           size=wx.Size(Constants.plain_text_dialog_width, Constants.plain_text_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Text field sizer
        self._text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._field_text = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self._text_sub_sizer.Add(self._field_text, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._text_sub_sizer, 1, flag=wx.EXPAND)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._save_button = wx.Button(self, wx.ID_OK, Strings.button_save)
        self._save_button.SetDefault()
        grouping_sizer.Add(self._save_button)
        grouping_sizer.Add(wx.Size(Constants.default_border, Constants.default_border))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Constants.default_border)
        self._horizontal_sizer.Add(self._vertical_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Constants.default_border)
        self.SetSizer(self._main_vertical_sizer)
        self.SetTitle(f'{Strings.dialog_edit.format(word_list)}')
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, save the file.
        :param event: The button event
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            print('TODO save')

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        print('TODO')
