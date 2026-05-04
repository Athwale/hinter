import re
from typing import List, Dict

import bs4
import htmlmin
from bs4 import Tag, NavigableString
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
        self._words: Dict = {}
        self._word_count: int = 0
        self._plain_text: str = ''
        self._errors: List[str] = []
        self._new: bool = True

        self._word_matcher = re.compile(r"(\w[\w']*\w|\w)")

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

    def get_parsed_text(self) -> List:
        """
        Return the parsed text prepared for loading into giu.
        :return: The parsed text prepared for loading into gui.
        """
        return self._converted

    def get_word_count(self) -> int:
        """
        Return the number of words in last saved text.
        :return: the number of words in last saved text.
        """
        return self._word_count

    def get_word_dict(self) -> Dict[str, int]:
        """
        Return a dictionary of unique words and their counts.
        :return: a dictionary of unique words and their counts.
        """
        return self._words

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
        Set new converted text representation. Call before saving with the newly converted document.
        :param converted: New list of tuples.
        :return: None
        """
        self._converted = converted

    def split_words(self, plain_text: str) -> None:
        """
        Split text into words and fill a dictionary with how often they show up.
        :param plain_text: Plain text from stc.
        :return: None
        """
        # todo here
        self._plain_text = plain_text.lower()
        words = self._word_matcher.findall(self._plain_text)
        self._word_count = len(words)
        words_set = set(words)

        for w in words_set:
            # todo ignore some words, have a limit where words are too repeated.
            self._words[w] = self._plain_text.count(w)

        # todo dialog with a sorted list.
        print(self._words)

    def read_document(self) -> None:
        """
        Parse document and fill internal variables.
        # todo read metadata from the file too.
        :return: None
        :raises PermissionError if file is not accessible
        :raises FormatError if formatting marks are not evenly matched.
        """
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
        Create a new HTML from the document. Call set_converted() first with new converted document from the gui.
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
            return False
        except (PermissionError, OSError) as e:
            raise PermissionError(e)

    def __str__(self):
     return f"Path: {self._path}\nText: {self._raw_html_text}"