from pathlib import Path

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
        self._size: str = f"{Constants.main_window_size.width},{Constants.main_window_size.height}"

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
        # todo handle exceptions and test.
        # todo load size and position
        try:
            if self._config_file.exists() and self._config_file.is_file():
                with open(self._config_file, 'r', encoding="utf-8") as config:
                    for line in config.readlines():
                        if line.startswith('last-file:'):
                            file = line.split(":")[1].replace('\n', '').strip()
                            self._last_file = Path(file)
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

    def save_config(self) -> None:
        """
        Save config file.
        :return: None
        :raises PermissionError if file access is not possible.=
        """
        # todo test exceptions.
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
            config.write(f"size: {self._size}\n")
