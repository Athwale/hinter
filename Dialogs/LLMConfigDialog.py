from urllib.parse import urlparse

import wx

from Constants import Constants, Strings
from Tools.Config import Config


class LLMConfigDialog(wx.Dialog):

    def __init__(self, parent, config: Config):
        """
        Configuration dialog for LLM connection.
        :param parent: The window that created the dialog.
        :param config: Config instance.
        """
        wx.Dialog.__init__(self, parent, title=Strings.dialog_llm,
                           size=wx.Size(Constants.plain_text_dialog_width, Constants.plain_text_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._config = config

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._field_url = wx.TextCtrl(self, -1)
        self._label_llm_url = wx.StaticText(self, -1, label=Strings.label_url_port)
        self._field_system_prompt = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE, size=wx.Size(-1, 100))
        self._label_system_prompt = wx.StaticText(self, -1, label=Strings.label_system_prompt)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._save_button = wx.Button(self, wx.ID_OK, Strings.button_save)
        self._save_button.SetDefault()
        grouping_sizer.Add(self._save_button)
        grouping_sizer.Add(wx.Size(Constants.default_border, Constants.default_border))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._main_vertical_sizer.Add(self._label_llm_url, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._field_url, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._label_system_prompt, 0, flag=wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._field_system_prompt, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Constants.default_border)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Constants.default_border)
        self.SetSizer(self._main_vertical_sizer)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, save and validate the config.
        :param event: The button event used to tell which button was pressed.
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            url = self._field_url.GetValue()
            try:
                result = urlparse(url)
                if result.scheme not in ('http', 'https') or not result.netloc or ":" not in result.netloc:
                    self._label_llm_url.SetForegroundColour(wx.RED)
                    return
                int(result.netloc.split(":")[1])
            except ValueError:
                self._label_llm_url.SetForegroundColour(wx.RED)
                return
            self._config.set_llm_url(url)
            self._config.set_llm_system_prompt(self._field_system_prompt.GetValue())
            self._config.save_config()
            event.Skip()
        elif event.GetId() == wx.ID_CANCEL:
            # Skip event to let it go into the main thread and close this dialog.
            event.Skip()

    def _display_dialog_contents(self) -> None:
        """
        Display the config page.
        :return: None
        """
        self._field_url.SetValue(self._config.get_llm_url())
        self._field_system_prompt.SetValue(self._config.get_llm_system_prompt())
