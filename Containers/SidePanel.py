from typing import List

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
        # Disable all panels by default, assigning indicators will enable them.
        panel = ListItemPanel(self, item, False)
        self._sizer.Add(panel, 0, wx.EXPAND)
        # This is some sort of hack co we can keep the created panels and the sizer does not complain later when we
        # re-add them.
        self._sizer.Detach(panel)
        panel.update_count()
        panel.Show(False)
        return panel

    def add_items(self, items: List[ListItemPanel]) -> None:
        """
        Add new items to the list.
        :param items: Dictionary of items with ids.
        :return: None
        """
        # Add items from most repetitions to least.
        # The items are added to the sizer above unordered and show up unordered. They are detached in clear_list and
        # reinserted in order here.
        insert_later: List[ListItemPanel] = []
        index = 0
        for item in sorted(items):
            item.update_count()
            item.Show(True)
            if not item.get_word_instance().has_indicator():
                item.set_enabled(False)
            if item.get_word_instance().is_selected():
                # Group selected words at the top.
                self._sizer.Insert(0, item, 0, wx.EXPAND)
                index += 1
            else:
                insert_later.append(item)

        for item in insert_later:
            # Insert unselected words.
            self._sizer.Insert(index, item, 0, wx.EXPAND)

        self._sizer.Layout()
        self.SetupScrolling(scroll_x=False, scrollToTop=False)

    def clear_list(self) -> None:
        """
        Clear all items from list. But do not delete them.
        :return: None
        """
        for ch in self.GetChildren():
            ch: ListItemPanel
            ch.Show(False)
            self._sizer.Detach(ch)
        self.Layout()

    def wipe_list(self) -> None:
        """
        Delete all items from list.
        :return: None
        """
        for ch in self.GetChildren():
            ch: ListItemPanel
            ch.Show(False)
            self._sizer.Detach(ch)
            ch.Destroy()
        self.Layout()
