from pathlib import Path
from typing import List

from Constants import Constants, Strings
from Exceptions.FormatError import FormatError


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
        :raises PermissionError if file is not accessible
        :raises FormatError if formatting marks are not evenly matched.
        """
        # todo handle exceptions.
        # todo switch to html which can be opened in open office and keep formatting
        try:
            if self._path.exists() and self._path.is_file():
                with open(self._path, "r") as f:
                    self._text = f.read()
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

        stack: List[str] = []
        for c in self._text:
            if c == Constants.mark_bold:
                if stack:
                    if stack[-1] == Constants.mark_bold:
                        stack.pop()
                else:
                    stack.append(c)
            elif c == Constants.mark_italic:
                if stack:
                    if stack[-1] == Constants.mark_italic:
                        stack.pop()
                else:
                    stack.append(c)
            else:
                pass

        if stack:
            # There is something left in the stack, formating markers are mismatched.
            raise FormatError(Strings.err_file_format)

    def __str__(self):
     return f"Path: {self._path}\nText: {self._text}"