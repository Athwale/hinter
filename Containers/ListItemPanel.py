import wx
from wx import Size

from Constants import Constants
from Constants.Constants import CheckboxChangedEvent
from Containers.Word import Word


class ListItemPanel(wx.Panel):
    """
    Custom panel for word list items.
    """

    def __init__(self, parent, word: Word, state: bool):
        """
        List item constructor.
        :param parent: Parent control.
        :param word: Word instance.
        :param state: Initial checkbox state.
        """

        super().__init__(parent, -1)

        self._word_instance: Word = word

        self._h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self._check_box = wx.CheckBox(self, -1)
        self._check_box.SetValue(state)
        self._word_label = wx.StaticText(self, -1, self._word_instance.get_word().decode('utf-8'),
                                         style=wx.ST_ELLIPSIZE_MIDDLE,
                                         size=Size(120, -1))
        self._count = wx.StaticText(self, -1, str(self._word_instance.get_count()), style=wx.ST_ELLIPSIZE_END)

        self._h_sizer.Add(self._check_box, 0, wx.ALL, Constants.default_border)
        self._h_sizer.Add(self._word_label, 0, wx.TOP | wx.BOTTOM, Constants.default_border)
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
        self._word_instance.set_selected(self._check_box.GetValue())
        evt = CheckboxChangedEvent(self.GetId())
        if self._check_box.IsChecked():
            evt.SetInt(1)
            evt.SetClientObject(self._word_label)
        else:
            evt.SetInt(0)
            evt.SetClientObject(self._word_label)
        wx.PostEvent(self.GetEventHandler(), evt)

    def update_count(self) -> None:
        """
        Update the number of words for the item.
        :return: None
        """
        self._count.SetLabel(str(self._word_instance.get_count()))

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
        self._word_label = value

    def set_checked(self, state: bool) -> None:
        """
        Set the checkbox state and set the Word's selected state.
        :param state: True to check.
        :return: None
        """
        self._check_box.SetValue(state)
        self._word_instance.set_selected(state)

    def is_checked(self) -> bool:
        """
        Returns True if the checkbox is checked.
        :return: True if the checkbox is checked.
        """
        return self._check_box.IsChecked()

    def is_enabled(self) -> bool:
        """
        Return True if the item is clickable.
        :return: True if the item is clickable.
        """
        return self._check_box.IsEnabled()

    def set_enabled(self, state: bool) -> None:
        """
        Set the item to Enabled or Disabled state.
        :param state: True / False
        :return: None
        """
        if state:
            self._check_box.Enable(True)
            self._word_label.SetForegroundColour(Constants.color_black)
        else:
            self._check_box.Enable(False)
            self._word_label.SetForegroundColour(Constants.color_grey)

    def __str__(self):
        return f"Item panel: Checked: {self.is_checked()}, Enabled: {self.is_enabled()}, Word: {self._word_instance}"

    # Sorts words by count not by alphabet order.
    def __eq__(self, other):
        if not isinstance(other, ListItemPanel):
            return NotImplemented
        return self._word_instance.get_count() == other.get_word().get_count()

    def __lt__(self, other):
        if not isinstance(other, ListItemPanel):
            return NotImplemented
        return self._word_instance.get_count() < other.get_word().get_count()