from typing import List

import bs4
from bs4 import Tag, NavigableString
from wx import richtext
from pathlib import Path

from Constants import Constants
from Resources.Fetch import Fetch


class Document:
    """
    Carrier class for currently loaded document file.
    # todo add the metadata to a div? Same file.
    """

    def __init__(self, path: Path):
        """
        Document constructor.
        :param path: Path to the document.
        """
        self._path: Path = path
        self._raw_html_text: str = ""
        self._converted: List = []
        self._new: bool = True

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
        return self._raw_html_text

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

# ----------------------------------------------------------------------------------------------------------------------

    def set_path(self, path: Path) -> None:
        """
        Set new file path.
        :param path: New file path.
        :return: None
        """
        self._path = path

    def set_converted(self, converted: List) -> None:
        """
        Set new converted text representation.
        :param converted: New list of tuples.
        :return: None
        """
        self._converted = converted

    def read_document(self) -> None:
        """
        Parse document and fill internal variables and the rich text buffer.
        # todo read metadata from the file too.
        :return: None
        :raises PermissionError if file is not accessible
        :raises FormatError if formatting marks are not evenly matched.
        """
        # todo handle exceptions.
        # todo adapt to the new list format. This must ignore line breaks and only use br?
        try:
            if self._path.exists() and self._path.is_file():
                with open(self._path, "r", encoding="utf-8") as f:
                    self._raw_html_text = f.read()
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

        # todo ignore \n only use br. Remove \n from strings, this allows OpenOffice html to be loaded.
        soup = bs4.BeautifulSoup(self._raw_html_text, features="html.parser")
        body = soup.find(name="body")
        for ch in body.children:
            if isinstance(ch, Tag) and ch.name == 'p':
                # These can also be NavigableString and those are leftover \n.
                for element in ch.children:
                    if isinstance(element, NavigableString):
                        self._converted.append((Constants.style_default, element.text))
                    elif isinstance(element, Tag):
                        # todo handle even the other way around
                        if element.name == "b":
                            style = Constants.style_bold
                            if element.next_element.name == "i":
                                style = Constants.style_bold_italic
                            self._converted.append((style, element.text))
                        if element.name == "i":
                            self._converted.append((Constants.style_italic, element.text))
                        if element.name == "br":
                            self._converted.append((Constants.style_break, ""))
                    else:
                        # todo handle exception
                        print(element)
        self._new = False

    def save_document(self) -> bool:
        """
        Create a new HTML from the document.
        # TODO test exceptions.
        :return: True if saved successfully.
        """
        # Create a new html file to fill up from the template.

        with open(Fetch.get_resource_path('template.html'), "r", encoding="utf-8") as f:
            self._raw_html_text = f.read()

        soup = bs4.BeautifulSoup(self._raw_html_text, features="html.parser")
        body: Tag = soup.find(name="body")
        # Everything is in one paragraph, the rest is solved by <br>
        par = soup.new_tag("p")

        for chunk in self._converted:
            if chunk[0] == Constants.style_default:
                par.append(bs4.NavigableString(chunk[1]))
            elif chunk[0] == Constants.style_italic:
                i = soup.new_tag('i')
                i.string = chunk[1]
                par.append(i)
            elif chunk[0] == Constants.style_bold:
                b = soup.new_tag('b')
                b.string = chunk[1]
                par.append(b)
            elif chunk[0] == Constants.style_bold_italic:
                b = soup.new_tag('b')
                i = soup.new_tag('i')
                i.string = chunk[1]
                b.append(i)
                par.append(b)
        body.append(par)

        # Replace \n with <br> in the whole file.
        for element in par.descendants:
            if isinstance(element, NavigableString):
                replacement = element.string.replace("\n", "<br>")
                element.replace_with(bs4.BeautifulSoup(replacement, "html.parser"))

        try:
            if self._path.exists() and self._path.is_file():
                with open(self._path, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                    return True
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

    def __str__(self):
     return f"Path: {self._path}\nText: {self._raw_html_text}"