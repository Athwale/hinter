import wx

from Constants import Constants, Strings
from Containers.Document import Document


class PlainTextEditDialog(wx.Dialog):

    def __init__(self, parent, word_list: str, document: Document):
        """
        Show a simple plain text editor with a file opened with the ability to save the file.
        Used for word lists.
        :param parent: Parent frame.
        :param word_list: Word list name
        :param document: Document instance
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_edit,
                           size=wx.Size(Constants.plain_text_dialog_width, Constants.plain_text_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._document = document
        self._list_type = word_list

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

        self._illegal_characters_ignored = '.,; '
        self._illegal_characters_synonym = '.; '

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, save the file.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            if (self._list_type == Strings.menu_item_edit_words_ignored_hint or
                    self._list_type == Strings.menu_item_edit_words_names_hint):
                words = self._field_text.GetValue().split('\n')
                for w in words:
                    # Skip empty strings
                    if w:
                        for ch in self._illegal_characters_ignored:
                            if ch in w:
                                wx.MessageBox(Strings.warn_word_format_single,
                                              Strings.status_warning, wx.OK | wx.ICON_WARNING)
                                return
                new_set = set()
                for w in words:
                    if w:
                        new_set.add(w.lower().strip())
                if self._list_type == Strings.menu_item_edit_words_names_hint:
                    self._document.set_names(new_set)
                elif self._list_type == Strings.menu_item_edit_words_ignored_hint:
                    self._document.set_ignored_words(new_set)
                # Skip event to let it go into the main thread and close this dialog.
                event.Skip()
            elif self._list_type == Strings.menu_item_edit_words_synonyms_hint:
                synonyms = self._field_text.GetValue().split('\n')
                for group in synonyms:
                    if group:
                        for word in group.split(','):
                            for ch in self._illegal_characters_synonym:
                                if ch in word.strip():
                                    wx.MessageBox(Strings.warn_word_format_synonym,
                                                  Strings.status_warning, wx.OK | wx.ICON_WARNING)
                                    return
                new_list = []
                for group in synonyms:
                    if group:
                        new_set = set()
                        for word in group.split(','):
                            new_set.add(word.strip())
                        new_list.append(new_set)
                self._document.set_synonyms(new_list)
                event.Skip()
        elif event.GetId() == wx.ID_CANCEL:
            event.Skip()
            return

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        if self._list_type == Strings.menu_item_edit_words_ignored_hint:
            for w in sorted(self._document.get_ignored_words()):
                self._field_text.AppendText(f"{w}\n")
        elif self._list_type == Strings.menu_item_edit_words_names_hint:
            for w in sorted(self._document.get_names()):
                self._field_text.AppendText(f"{w.capitalize()}\n")
        elif self._list_type == Strings.menu_item_edit_words_synonyms_hint:
            for group in sorted(self._document.get_synonyms()):
                string = ', '.join(group)
                self._field_text.AppendText(f"{string}\n")
