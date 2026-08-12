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

        # Values
        values_sizer = wx.BoxSizer(wx.VERTICAL)
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        size = wx.Size(180, -1)
        # Max number of tokens to generate.
        self._max_tokens = wx.SpinCtrl(self, id=wx.ID_ANY,
                                       value=str(Constants.config_llm_tokens_default),
                                       style=wx.SP_ARROW_KEYS,
                                       size=size,
                                       min=Constants.config_llm_tokens_min,
                                       max=Constants.config_llm_tokens_max,
                                       initial=Constants.config_llm_tokens_default)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_max_tokens)
        item_sizer.Add(self._max_tokens)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

        # Number of responses to generate.
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._n = wx.SpinCtrl(self, id=wx.ID_ANY,
                              value=str(Constants.config_llm_responses_default),
                              style=wx.SP_ARROW_KEYS,
                              size=size,
                              min=Constants.config_llm_responses_min,
                              max=Constants.config_llm_responses_max,
                              initial=Constants.config_llm_responses_default)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_num_responses)
        item_sizer.Add(self._n)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

        # Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more
        # focused and deterministic.
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._temperature = wx.SpinCtrlDouble(self, id=wx.ID_ANY,
                                              value=str(Constants.config_llm_temp_default),
                                              style=wx.SP_ARROW_KEYS,
                                              size=size,
                                              min=Constants.config_llm_temp_min,
                                              max=Constants.config_llm_temp_max,
                                              initial=Constants.config_llm_temp_default,
                                              inc=0.1)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_temp)
        item_sizer.Add(self._temperature)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

        # Positive values penalize new tokens based on whether they appear in the text so far, increasing the model’s
        # likelihood to talk about new topics.
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._presence_penalty = wx.SpinCtrlDouble(self, id=wx.ID_ANY,
                                                   value=str(Constants.config_llm_presence_pen_default),
                                                   style=wx.SP_ARROW_KEYS,
                                                   size=size,
                                                   min=Constants.config_llm_presence_pen_min,
                                                   max=Constants.config_llm_presence_pen_max,
                                                   initial=Constants.config_llm_presence_pen_default,
                                                   inc=0.1)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_presence_penalty)
        item_sizer.Add(self._presence_penalty)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

        # Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the
        # model’s likelihood to repeat the same line verbatim.
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._frequency_penalty = wx.SpinCtrlDouble(self, id=wx.ID_ANY,
                                                    value=str(Constants.config_llm_frequency_pen_default),
                                                    style=wx.SP_ARROW_KEYS,
                                                    size=size,
                                                    min=Constants.config_llm_frequency_pen_min,
                                                    max=Constants.config_llm_frequency_pen_max,
                                                    initial=Constants.config_llm_frequency_pen_default,
                                                    inc=0.1)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_frequency_penalty)
        item_sizer.Add(self._frequency_penalty)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

        # Verbosity
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._verbosity = wx.SpinCtrl(self, id=wx.ID_ANY,
                              value=str(Constants.config_llm_verbosity_default),
                              style=wx.SP_ARROW_KEYS,
                              size=size,
                              min=Constants.config_llm_verbosity_min,
                              max=Constants.config_llm_verbosity_max,
                              initial=Constants.config_llm_verbosity_default)
        max_tokens_label = wx.StaticText(self, -1, Strings.label_verbosity)
        item_sizer.Add(self._verbosity)
        item_sizer.Add(max_tokens_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=Constants.default_border)
        values_sizer.Add(item_sizer, flag=wx.BOTTOM, border=Constants.default_border)

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
        self._main_vertical_sizer.Add(values_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
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
            self._config.set_llm_tokens(self._max_tokens.GetValue())
            self._config.set_llm_responses(self._n.GetValue())
            self._config.set_llm_frequency_p(self._frequency_penalty.GetValue())
            self._config.set_llm_presence_p(self._presence_penalty.GetValue())
            self._config.set_llm_temperature(self._temperature.GetValue())
            self._config.set_llm_verbosity(self._verbosity.GetValue())
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
        self._max_tokens.SetValue(self._config.get_llm_tokens())
        self._n.SetValue(self._config.get_llm_responses())
        self._frequency_penalty.SetValue(self._config.get_llm_frequency_p())
        self._presence_penalty.SetValue(self._config.get_llm_presence_p())
        self._temperature.SetValue(self._config.get_llm_temperature())
        self._verbosity.SetValue(self._config.get_llm_verbosity()[0])
