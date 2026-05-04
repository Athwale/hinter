from typing import Dict

import wx
import wx.html
from wx import Size

from Constants import Strings, Constants


class WordInfoDialog(wx.Dialog):

    def __init__(self, parent, words: Dict[str, int]):
        """
        Display a dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_words_info,
                           size=Size(Constants.words_dialog_width, Constants.words_dialog_height))
        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self._html_window = wx.html.HtmlWindow(self)
        if 'gtk2' in wx.PlatformInfo:
            self._html_window.SetStandardFonts()

        self._close_button = wx.Button(self, wx.ID_OK, Strings.button_close)
        self._close_button.SetDefault()

        # todo here
        self._html_window.SetPage(str(words))

        self._main_vertical_sizer.Add(self._html_window, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._close_button, flag=wx.EXPAND)
        self.SetSizer(self._main_vertical_sizer)

        self.ShowModal()
        self.Destroy()
