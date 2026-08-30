import wx

from Constants import Constants, Strings
from Containers.Document import Document


class NotesEditorDialog(wx.Dialog):

    def __init__(self, parent, document: Document):
        """
        Show a simple plain text editor with a file opened with the ability to save the file.
        Used for word lists.
        :param parent: Parent frame.
        :param document: Document instance
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_edit, style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX)

        self._document = document

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetMinSize(wx.Size(Constants.plain_text_dialog_width, Constants.plain_text_dialog_height))
        self.SetInitialSize(wx.Size(Constants.plain_text_dialog_width, Constants.plain_text_dialog_height))
        self._field_text = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._save_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._save_button.SetDefault()
        grouping_sizer.Add(self._save_button)
        grouping_sizer.Add(wx.Size(Constants.default_border, Constants.default_border))
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._main_vertical_sizer.Add(self._field_text, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Constants.default_border)
        self.SetSizer(self._main_vertical_sizer)
        self.SetTitle(Strings.dialog_notes)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_TEXT, self._text_changed, self._field_text)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, save the file.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            self._document.set_notes(self._field_text.GetValue())
            self._document.set_modified(True)
            # todo let the main frame know it closed and was edited.
            event.Skip()

    # noinspection PyUnusedLocal
    def _text_changed(self, event: wx.CommandEvent) -> None:
        """
        Handle text changes and save to document.
        :param event: Not used
        :return: None
        """
        self._document.set_notes(self._field_text.GetValue())

    def _display_dialog_contents(self) -> None:
        """
        Load words into the dialog text field.
        :return: None
        """
        self._field_text.SetValue(self._document.get_notes())
        self._field_text.SetInsertionPoint(-1)
