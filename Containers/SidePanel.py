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
        self.SetupScrolling(scroll_x=False, scrollToTop=False)
        self.SetSizer(self._sizer)
        self.Layout()

    def add_item(self, index: int, word: Word) -> None:
        """
        Add new item to the list.
        :param index: Item index.
        :param word: Word instance.
        :return: None
        """
        # todo forward the info to the item.
        # todo delete item
        # todo clear list Hide, Remove, Destroy, Layout.
        self._sizer.Add(ListItemPanel(self), 0, wx.EXPAND)
        self.Layout()
