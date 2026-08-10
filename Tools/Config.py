from pathlib import Path
from typing import Tuple

import wx

from Constants import Constants, Strings


class Config:
    """
    Very simple plain text config file helper.
    """

    def __init__(self):
        """
        Config manager class constructor.
        """
        self._config_file = Constants.config_file
        self._last_file: Path = Path()
        self._position_x: int = 0
        self._position_y: int = 0
        self._width: int = Constants.main_window_size.width
        self._height: int = Constants.main_window_size.height

        self._llm_url: str = Constants.llm_default_url
        self._llm_system_prompt: str = Constants.llm_system_prompt
        self._llm_tokens: int = Constants.config_llm_tokens_default
        self._llm_responses: int = Constants.config_llm_responses_default
        self._llm_temperature: float = Constants.config_llm_temp_default
        self._llm_presence_p: float = Constants.config_llm_presence_pen_default
        self._llm_frequency_p: float = Constants.config_llm_frequency_pen_default
        self._llm_verbosity: int = Constants.config_llm_verbosity_default

        if not self._config_file.exists():
            # Create a new default file.
            self._save()
        self.load_config()

    def load_config(self) -> None:
        """
        Load values from config file.
        :return: None
        :raises PermissionError if file access is not possible.
        """
        try:
            if self._config_file.exists() and self._config_file.is_file():
                with open(self._config_file, 'r', encoding="utf-8") as config:
                    for line in config.readlines():
                        if line.startswith('last-file:'):
                            file = line.split(":")[1].replace('\n', '').strip()
                            self._last_file = Path(file)
                        if line.startswith('position:'):
                            self._position_x, self._position_y = line.split(":")[1].replace('\n', '').strip().split(',')
                            try:
                                self._position_x = int(self._position_x)
                                self._position_y = int(self._position_y)
                            except ValueError as _:
                                self._position_x = 0
                                self._position_y = 0
                        if line.startswith('size:'):
                            self._width, self._height = line.split(":")[1].replace('\n', '').strip().split(',')
                            try:
                                self._width = int(self._width)
                                self._height = int(self._height)
                            except ValueError as _:
                                self._width = Constants.main_window_size.width
                                self._height = Constants.main_window_size.height

                        if line.startswith('llm_url:'):
                            url = line.split(" ")[1].replace('\n', '').strip()
                            self._llm_url = url
                        if line.startswith('llm_system_prompt:'):
                            # Todo what if we have more : in the string.
                            self._llm_system_prompt = line.split(":")[1].replace('\n', '').strip()
                        if line.startswith('llm_tokens:'):
                            try:
                                self._llm_tokens = int(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_tokens = Constants.config_llm_tokens_default
                        if line.startswith('llm_responses:'):
                            try:
                                self._llm_responses = int(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_responses = Constants.config_llm_responses_default
                        if line.startswith('llm_temperature:'):
                            try:
                                self._llm_temperature = float(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_temperature = Constants.config_llm_temp_default
                        if line.startswith('llm_presence_p:'):
                            try:
                                self._llm_presence_p = float(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_presence_p = Constants.config_llm_presence_pen_default
                        if line.startswith('llm_frequency_p:'):
                            try:
                                self._llm_frequency_p = float(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_frequency_p = Constants.config_llm_frequency_pen_default
                        if line.startswith('llm_verbosity:'):
                            try:
                                self._llm_verbosity = int(line.split(":")[1].replace('\n', '').strip())
                            except ValueError as _:
                                self._llm_verbosity = Constants.config_llm_verbosity_default
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

    def get_last_file(self) -> Path:
        """
        Get last opened file from config.
        :return: Path to file.
        """
        return self._last_file

    def set_last_file(self, file: Path) -> None:
        """
        Set new last opened file. Call save_config afterward.
        :param file: File path.
        :return: None
        """
        self._last_file = file

    def set_llm_url(self, url: str) -> None:
        """
        Set new LLM url.
        :param url: Network url.
        :return: None
        """
        self._llm_url = url

    def get_llm_url(self) -> str:
        """
        Get LLM url.
        :return: LLM url.
        """
        return self._llm_url

    def set_llm_system_prompt(self, prompt: str) -> None:
        """
        Set new LLM system prompt.
        :param prompt: New system prompt
        :return: None
        """
        new_prompt = ' '.join(line.strip() for line in prompt.split('\n'))
        self._llm_system_prompt = new_prompt

    def get_llm_system_prompt(self) -> str:
        """
        Get LLM system prompt.
        :return: LLM system prompt.
        """
        return self._llm_system_prompt

    def set_llm_tokens(self, tokens: int) -> None:
        """
        Set new LLM max tokens.
        :param tokens: Max tokens.
        :return: None
        """
        self._llm_tokens = tokens

    def get_llm_tokens(self) -> int:
        """
        Get LLM max tokens.
        :return: LLM max tokens.
        """
        return self._llm_tokens

    def set_llm_responses(self, responses: int) -> None:
        """
        Set new LLM number of responses.
        :param responses: Number of responses.
        :return: None
        """
        self._llm_responses = responses

    def get_llm_responses(self) -> int:
        """
        Get LLM number of responses.
        :return: LLM number of responses.
        """
        return self._llm_responses

    def set_llm_temperature(self, temperature: float) -> None:
        """
        Set new LLM temperature.
        :param temperature: Temperature value.
        :return: None
        """
        self._llm_temperature = temperature

    def get_llm_temperature(self) -> float:
        """
        Get LLM temperature.
        :return: LLM temperature.
        """
        return self._llm_temperature

    def set_llm_presence_p(self, presence_p: float) -> None:
        """
        Set new LLM presence penalty.
        :param presence_p: Presence penalty value.
        :return: None
        """
        self._llm_presence_p = presence_p

    def get_llm_presence_p(self) -> float:
        """
        Get LLM presence penalty.
        :return: LLM presence penalty.
        """
        return self._llm_presence_p

    def set_llm_frequency_p(self, frequency_p: float) -> None:
        """
        Set new LLM frequency penalty.
        :param frequency_p: Frequency penalty value.
        :return: None
        """
        self._llm_frequency_p = frequency_p

    def get_llm_frequency_p(self) -> float:
        """
        Get LLM frequency penalty.
        :return: LLM frequency penalty.
        """
        return self._llm_frequency_p

    def set_llm_verbosity(self, verbosity: int) -> None:
        """
        Set new LLM verbosity.
        :param verbosity: Verbosity level.
        :return: None
        """
        self._llm_verbosity = verbosity

    def get_llm_verbosity(self) -> Tuple[int, str]:
        """
        Get LLM verbosity.
        :return: LLM verbosity level.
        """
        if self._llm_verbosity == 2:
            return 2, 'medium'

        if self._llm_verbosity == 3:
            return 3, 'high'

        return 1, 'low'

    def get_size(self) -> wx.Size:
        """
        Return last saved or default window size.
        :return: Last saved or default window size.
        """
        return wx.Size(self._width, self._height)

    def set_size(self, size: wx.Size) -> None:
        """
        Set new window size.
        :param size: Size object.
        :return: None
        """
        self._width = size.width
        self._height = size.height

    def get_position(self) -> wx.Point:
        """
        Return a tuple of last known window position.
        :return: Point(x, y)
        """
        return wx.Point(self._position_x, self._position_y)

    def set_position(self, x: int, y: int) -> None:
        """
        Set new window position to save.
        :param x: X
        :param y: Y
        :return: None
        """
        self._position_x = x
        self._position_y = y

    # ------------------------------------------------------------------------------------------------------------------

    def save_config(self) -> None:
        """
        Save config file.
        :return: None
        :raises PermissionError if file access is not possible.=
        """
        try:
            if self._config_file.exists() and self._config_file.is_file():
                self._save()
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

    def _save(self) -> None:
        """
        Save values into file.
        :return: None
        """
        with open(self._config_file, 'w', encoding="utf-8") as config:
            config.write(f"# Config file for {Strings.app_title.format('')}\n")
            config.write(f"last-file: {self._last_file}\n")
            config.write(f"position: {self._position_x},{self._position_y}\n")
            config.write(f"size: {self._width},{self._height}\n")

            config.write(f"llm_url: {self._llm_url}\n")
            config.write(f"llm_system_prompt: {self._llm_system_prompt}\n")
            config.write(f"llm_tokens: {self._llm_tokens}\n")
            config.write(f"llm_responses: {self._llm_responses}\n")
            config.write(f"llm_temperature: {self._llm_temperature}\n")
            config.write(f"llm_presence_p: {self._llm_presence_p}\n")
            config.write(f"llm_frequency_p: {self._llm_frequency_p}\n")
            config.write(f"llm_verbosity: {self._llm_verbosity}\n")
