from typing import Dict

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

    def add_item(self, item_id: int, word: Word) -> None:
        """
        Add a new item to the list.
        :param item_id: Item id.
        :param word: Word instance.
        :return: None
        """
        # todo delete item
        self._sizer.Add(ListItemPanel(self, word, item_id), 0, wx.EXPAND)
        self.SetupScrolling(scroll_x=False, scrollToTop=False)
        self.Layout()

    def add_items(self, items: Dict[int, Word]) -> None:
        """
        Add new items to the list.
        :param items: Dictionary of items with ids.
        :return: None
        """
        for i, w in items.items():
            self._sizer.Add(ListItemPanel(self, w, i), 0, wx.EXPAND)
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
