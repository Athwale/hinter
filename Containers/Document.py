from pathlib import Path


class Document:
    """
    Carrier class for currently loaded document file.
    """

    def __init__(self, path: Path):
        """
        Document constructor.
        :param path: Path to the document.
        """
        self._path: Path = path
        self._text: str = ""

    def get_path(self) -> Path:
        """
        Return current document path.
        :return: Current document path.
        """
        return self._path

    def get_raw_text(self) -> str:
        """
        Return current document text.
        :return: Current document text.
        """
        return self._text

    def read_document(self) -> None:
        """
        Parse document and fill internal variables.
        # todo read meta file too.
        :return: None
        """
        # todo handle no file, no access.
        with open(self._path, "r") as f:
            self._text = f.read()

        # todo parse and ensure consistent formatting. Stack based parser for marks?

    def __str__(self):
     return f"Path: {self._path}\nText: {self._text}"