import wx
from wx import Size

from Constants import Strings


class SavingWaitDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a dialog with a saving file message.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.status_saving,
                           size=Size(150, 50), style=wx.BORDER_NONE | wx.STAY_ON_TOP)
        self._main_vertical_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._busy_wheel = wx.ActivityIndicator(self, wx.ID_ANY, size=wx.Size(100, 100))
        self._busy_wheel.SetOwnForegroundColour(wx.Colour(0, 255, 0))
        self._label = wx.StaticText(self, label=Strings.status_loading)

        self._main_vertical_sizer.Add(self._label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        self._main_vertical_sizer.Add(self._busy_wheel, 0)
        self.SetSizer(self._main_vertical_sizer)

    def start(self, saving: bool) -> None:
        """
        Start the wheel and set dialog type.
        :param saving: If True the dialog will show a saving file message, otherwise loading.
        :return: None
        """
        if saving:
            self._busy_wheel.SetOwnForegroundColour(wx.Colour(0, 0, 255))
            self._label.SetLabelText(Strings.status_saving)
        self._busy_wheel.Start()
