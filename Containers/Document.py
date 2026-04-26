from typing import List

import bs4
import htmlmin
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
        self._errors: List[str] = []
        self._new: bool = True

    def get_path(self) -> Path:
        """
        Return current document path.
        :return: Current document path.
        """
        return self._path

    def get_errors(self) -> List[str]:
        """
        Return a list of errors from loading the document.
        :return: A list of errors from loading the document.
        """
        return self._errors

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
        self._errors = []
        try:
            if self._path.exists() and self._path.is_file():
                with open(self._path, "r", encoding="utf-8") as f:
                    self._raw_html_text = f.read()
                    # Odd behavior where <br/>\n is converted to an empty space at the start of the next line.
                    self._raw_html_text = self._raw_html_text.replace('<br/>\n', '<br/>')
                    # Help solve odd formating from OpenOffice.
                    self._raw_html_text = htmlmin.minify(self._raw_html_text,
                                                         remove_comments=True,
                                                         remove_empty_space=True)
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

        soup = bs4.BeautifulSoup(self._raw_html_text, features="html.parser")
        body = soup.find(name="body")
        for ch in body.children:
            if isinstance(ch, Tag) and ch.name == 'p':
                # These can also be NavigableString and those are leftover \n.
                for element in ch.children:
                    if isinstance(element, NavigableString):
                        self._converted.append((Constants.style_default, element.text))
                    elif isinstance(element, Tag):
                        if element.name == "b":
                            style = Constants.style_bold
                            if element.next_element.name == "i":
                                style = Constants.style_bold_italic
                            self._converted.append((style, element.text))
                        elif element.name == "i":
                            style = Constants.style_italic
                            if element.next_element.name == "b":
                                style = Constants.style_bold_italic
                            self._converted.append((style, element.text))
                        elif element.name == "br":
                            self._converted.append((Constants.style_break, ""))
                        else:
                            self._errors.append(str(element))
                    else:
                        self._errors.append(str(element))
            else:
                self._errors.append(str(ch))
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