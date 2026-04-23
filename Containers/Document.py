from typing import List

import bs4
from bs4 import Tag, NavigableString
from wx import richtext
from pathlib import Path


class Document:
    """
    Carrier class for currently loaded document file.
    # todo add the metadata to a div? Same file.
    """

    def __init__(self, path: Path, buffer: richtext.RichTextBuffer, handler: richtext.RichTextHTMLHandler):
        """
        Document constructor.
        :param path: Path to the document.
        :param buffer: richtext Buffer of the rich text control.
        :param handler richtext HTML handler of the rich text control.
        """
        self._buffer: richtext.RichTextBuffer = buffer
        self._handler: richtext.RichTextHTMLHandler = handler
        self._path: Path = path
        self._text: str = ""
        self._converted: List = []
        self._new: bool = True

    def get_path(self) -> Path:
        """
        Return current document path.
        :return: Current document path.
        """
        return self._path

    def set_path(self, path: Path) -> None:
        """
        Set new file path.
        :param path: New file path.
        :return: None
        """
        self._path = path

    def get_raw_text(self) -> str:
        """
        Return current document text.
        :return: Current document text.
        """
        return self._text

    def get_parsed_text(self) -> List:
        """
        Return the parsed text prepared for richtextctrl.
        :return: The parsed text prepared for richtextctrl.
        """
        return self._converted

    def is_new(self) -> bool:
        """
        Return True if this document was never saved.
        :return: True if this document was never saved.
        """
        return self._new

    def read_document(self) -> None:
        """
        Parse document and fill internal variables and the rich text buffer.
        # todo read metadata from the file too.
        :return: None
        :raises PermissionError if file is not accessible
        :raises FormatError if formatting marks are not evenly matched.
        """
        # todo handle exceptions.
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
                par: List = []
                for element in ch.children:
                    if isinstance(element, NavigableString):
                        par.append(("text", element.text))
                    elif isinstance(element, Tag):
                        if element.name == "b":
                            style = "bold"
                            if element.next_element.name == "i":
                                style = "bold_italic"
                            par.append((style, element.text))
                        if element.name == "i":
                            par.append(("italic", element.text))
                        if element.name == "br":
                            par.append(("break", ""))
                    else:
                        # todo handle exception
                        print(element)
                self._converted.append(par)
        self._new = False

    def save_document(self) -> bool:
        """

        :return: True if saved successfully.
        """
        # TODO test exceptions.
        if self._handler.SaveFile(self._buffer, str(self._path)):
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
                    self._new = False
                    return True
            else:
                return False
        else:
            return False

    def __str__(self):
     return f"Path: {self._path}\nText: {self._text}"