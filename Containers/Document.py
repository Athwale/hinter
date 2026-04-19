import bs4
from bs4 import Tag, NavigableString
from wx import richtext
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

    def read_document(self, buffer: richtext.RichTextBuffer) -> None:
        """
        Parse document and fill internal variables and the rich text buffer.
        # todo read meta file too.
        :param buffer buffer to fill with the data.
        :return: None
        :raises PermissionError if file is not accessible
        :raises FormatError if formatting marks are not evenly matched.
        """
        # todo handle exceptions.
        # todo switch to wxpython's HTML which can be opened in OpenOffice and keep formatting
        try:
            if self._path.exists() and self._path.is_file():
                with open(self._path, "r", encoding="utf-8") as f:
                    self._text = f.read()
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

        soup = bs4.BeautifulSoup(self._text, features="html.parser")
        body = soup.find(name="body")
        for ch in body.children:
            if isinstance(ch, Tag):
                # These can also be NavigableString and those are leftover \n.
                for element in ch.children:
                    print(type(element))

    def save_document(self, handler: richtext.RichTextHTMLHandler, buffer: richtext.RichTextBuffer) -> bool:
        """

        :return: True if saved successfully.
        """
        if handler.SaveFile(buffer, str(self._path)):
            soup = None
            with open(self._path, "r", encoding="utf-8") as html:
                soup = bs4.BeautifulSoup(html, features="html.parser")
                for font in soup.find_all(name="font"):
                    font.unwrap()
                for p in soup.find_all(name="p"):
                    p.attrs = {}
            if soup:
                with open(self._path, "w", encoding="utf-8") as html:
                    html.write(str(soup))
                    return True
            else:
                return False
        else:
            return False

    def __str__(self):
     return f"Path: {self._path}\nText: {self._text}"