from typing import Dict, List

import wx
import wx.lib.scrolledpanel
from wx._core import Size

from Constants import Constants
from Containers.ListItemPanel import ListItemPanel
from Containers.Word import Word


class SidePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    Side panel scrolled container.
    """

    def __init__(self, parent):
        """
        Side panel constructor.
        """
        super().__init__(parent, -1, size=Size(Constants.word_list_width, -1))

        self._parent = parent
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetAutoLayout(True)
        self.SetSizer(self._sizer)
        self.Layout()

    def add_item(self, word: ListItemPanel) -> None:
        """
        Add a new item to the list.
        :param word: Word instance.
        :return: None
        """
        # todo delete item
        self._sizer.Add(word, 0, wx.EXPAND)
        self.SetupScrolling(scroll_x=False, scrollToTop=False)
        self.Layout()

    def add_items(self, items: Dict[int, tuple[Word, bool]]) -> None:
        """
        Add new items to the list.
        :param items: Dictionary of items with ids.
        :return: None
        """
        # todo rewrite for list item
        for i, w in items.items():
            item_instance = ListItemPanel(self, w[0], w[1])
            if w[0].has_indicator():
                item_instance.set_active(True)
            else:
                item_instance.set_active(False)
            self._sizer.Add(item_instance, 0, wx.EXPAND)
        self.SetupScrolling(scroll_x=False, scrollToTop=False)
        self.Layout()

    def clear_list(self) -> None:
        """
        Clear all items from list.
        :return: None
        """
        for ch in self.GetChildren():
            ch.Hide()
            ch.Destroy()
        self.Layout()
