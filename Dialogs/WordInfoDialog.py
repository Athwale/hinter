from typing import Dict

import wx
import wx.html
from wx import Size

from Constants import Strings, Constants
from Containers.ListItemPanel import ListItemPanel


class WordInfoDialog(wx.Dialog):

    def __init__(self, parent, panels: Dict[bytes, ListItemPanel]):
        """
        Display a dialog with a word list and counts.
        :param parent: Parent frame.
        :param panels: Dictionary of [bytes, ListItemPanel]
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_words_info,
                           size=Size(Constants.words_dialog_width, Constants.words_dialog_height))
        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self._html_window = wx.html.HtmlWindow(self)
        if 'gtk2' in wx.PlatformInfo:
            self._html_window.SetStandardFonts()

        self._close_button = wx.Button(self, wx.ID_OK, Strings.button_close)
        self._close_button.SetDefault()

        content = ''
        for w, p in sorted(panels.items()):
            content += f'{w} -> {p.get_word_instance().get_count()}<br>'

        self._html_window.SetPage(content)

        self._main_vertical_sizer.Add(self._html_window, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._close_button,
                                      flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL,
                                      border=Constants.default_border)
        self.SetSizer(self._main_vertical_sizer)

        self.ShowModal()
        self.Destroy()
