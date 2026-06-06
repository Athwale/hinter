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

    def add_hidden_item(self, item: Word) -> ListItemPanel:
        """
        Add new item to the list in invisible state.
        :param item: Item to add
        :return: None
        """
        panel = ListItemPanel(self, item, True)
        self._sizer.Add(panel, 0, wx.EXPAND)
        panel.update_count()
        panel.Show(False)
        return panel

    def add_items(self, items: List[ListItemPanel]) -> None:
        """
        Add new items to the list.
        :param items: Dictionary of items with ids.
        :return: None
        """
        for item in items:
            item.update_count()
            item.Show(True)
        self.SetupScrolling(scroll_x=False, scrollToTop=False)

    def clear_list(self) -> None:
        """
        Clear all items from list.
        :return: None
        """
        for ch in self.GetChildren():
            ch: ListItemPanel
            ch.Show(False)
        self.Layout()
