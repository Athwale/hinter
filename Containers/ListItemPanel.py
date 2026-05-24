import wx
from wx import Size

from Constants import Constants
from Constants.Constants import CheckboxChangedEvent
from Containers.Word import Word


class ListItemPanel(wx.Panel):
    """
    Custom panel for word list items.
    """

    def __init__(self, parent, word: Word, item_id: int):
        """
        List item constructor.
        :param parent: Parent control.
        :param word: Word instance.
        :param item_id: Item id.
        """
        super().__init__(parent, -1)
        # todo handle checkbox clicks
        # todo add checkbox enabling/disabling

        self._word_instance: Word = word
        self._item_id: int = item_id

        self._h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self._check_box = wx.CheckBox(self, -1)
        self._word = wx.StaticText(self, -1, self._word_instance.get_word().decode('utf-8'),
                                   style=wx.ST_ELLIPSIZE_MIDDLE,
                                   size=Size(120, -1))
        self._count = wx.StaticText(self, -1, str(self._word_instance.get_count()), style=wx.ST_ELLIPSIZE_END)

        self._h_sizer.Add(self._check_box, 0, wx.ALL, Constants.default_border)
        self._h_sizer.Add(self._word, 0, wx.TOP | wx.BOTTOM, Constants.default_border)
        self._h_sizer.Add(wx.StaticLine(self, -1, size=Size(2, 26), style=wx.LI_HORIZONTAL))
        self._h_sizer.Add(self._count, 0, wx.TOP | wx.LEFT | wx.BOTTOM, Constants.default_border)

        self._v_sizer.Add(self._h_sizer, 1, wx.EXPAND)

        self._v_sizer.Add(wx.StaticLine(self, -1, size=wx.Size(Constants.word_list_width, -1)), 0)

        self._h_sizer.SetMinSize(wx.Size(Constants.word_list_width - 10, -1))
        self.SetSizer(self._v_sizer)

        self._h_sizer.Layout()

        self.Bind(wx.EVT_CHECKBOX, self._on_checkbox, self._check_box)

    def _on_checkbox(self, event: wx.CommandEvent) -> None:
        # Pass the event into the main window.
        evt = CheckboxChangedEvent(self.GetId())
        if self._check_box.IsChecked():
            evt.SetInt(1)
        else:
            evt.SetInt(0)
        wx.PostEvent(self.GetEventHandler(), evt)

    def get_word(self) -> Word:
        """
        Get the word.
        :return: The Word instance.
        """
        return self._word_instance

    def set_word(self, value: Word):
        """
        Set the word.
        :param value: The Word instance.
        """
        self._word = value

    def get_id(self) -> int:
        """
        Get the ID.
        :return: The ID.
        """
        return self._item_id

    def set_id(self, value: int):
        """
        Set the word.
        :param value: The word as bytes.
        """
        self._item_id = value