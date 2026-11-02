import datetime
import re
from collections import defaultdict
from threading import Thread
from typing import List, Tuple, Dict

import wx

from Constants import Strings, Constants
from Containers.Document import Document


class SaveFileThread(Thread):
    """
    Thread for saving the current document to disk.
    """

    def __init__(self, parent, document: Document, converted_text: List, plain_text: str,
                 word_distance: int, run_tests: bool) -> None:
        """
        Thread constructor.
        The editor is disabled during this operation.
        :param parent: The frame that called the thread.
        :param document: The document instance to save.
        :param converted_text: Data prepared for saving.
        :param plain_text: Plain text for additional tests.
        :param word_distance: Minimum two repetition word distance.
        :param run_tests: Run or do not run tests.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._document = document
        # Using the text field here is not thread safe. Gui methods can not be called form background threads safely.
        self._converted_text = converted_text
        self._plain_text = plain_text
        self._word_counts: Dict[bytes, int] = {}
        self._run_tets = run_tests
        self._min_word_distance = word_distance
        self.start()

    def run(self) -> None:
        """
        Run the file saving task and post an event back to the main thread.
        :return: None
        """
        self._document.set_converted(self._converted_text)
        try:
            if self._document.save_document():
                wx.CallAfter(self._parent.save_document_callback, True)
            else:
                wx.CallAfter(self._parent.save_document_callback, False)
        except PermissionError as _:
            wx.CallAfter(self._parent.save_document_callback, False)
            return

        d1 = datetime.datetime.now()
        print('start')
        if self._run_tets:
            errors = []
            # todo Stream error messages into main thread.
            # todo Can we parallelize with thread executor one thread for each test on whole text? beware of PIL.

            if self._document.get_names():
                errors.extend(self._check_names())
                errors.extend(self._check_name_lines())
            else:
                pass
                # check_fails[Constants.report_names_capitalized] = [(Strings.report_names_not_configured_lines, -1)]
                # check_fails[Constants.report_name_lines] = [(Strings.report_names_not_configured_caps, -1)]
                # todo append warning messages
            errors.extend(self._check_leftover())
            errors.extend(self._check_repetitions())
            errors.extend(self._check_similar_words())
            errors.extend(self._check_word_distance())

            # check_fails[Constants.report_close_words].extend(self._check_word_distance())
            # wx.CallAfter(self._parent.document_test_callback, check_fails)
            print('stop', datetime.datetime.now() - d1)

    def _find_stub(self, position: int) -> str:
        """
        Find a part of a line where the supposed problem might be located.
        :param position: Position in full text.
        :return: Stub of the line.
        """
        stub = self._plain_text[position - 25:position + 25]
        return stub.replace('\n', ' ')

    def _check_word_distance(self) -> List[Tuple[str, int, str, str]]:
        """
        Check for words with 2 repetitions that are too close together.
        :return: List of reports found (type, start position, stub, word or error)
        """
        # todo rewrite this to the new format.
        # Recalculate lines by word here to have the freshest data.
        plain_text = self._plain_text.lower().encode('utf-8')
        word_spans = list(Constants.word_matcher.finditer(plain_text))

        # Defaultdict wll create a new empty list if the key does not exist and add it into it. Otherwise, it
        # will just add the word to the existing list under that key.
        # Create a dictionary of words as bytes and a list of lines where the word is.
        lines_by_word: defaultdict[bytes, List[int]] = defaultdict(list)
        line_counter = 1
        for word_span in word_spans:
            word_bytes = word_span.group()
            if word_bytes == b"\n":
                line_counter += 1
            lines_by_word[word_bytes].append(line_counter)

        errors: List[Tuple[str, int, str, str]] = []
        for word, lines in lines_by_word.items():
            if len(lines) == 2:
                # Run this for words with just two repetitions, the rest is visible in the gui coloring tool.
                if (lines[1] - lines[0]) <= self._min_word_distance:
                    errors.append((Strings.report_word_distance.format(word.decode('utf-8'), lines[0], lines[1]),
                                   lines[0]))
        return errors

    def _check_name_lines(self) -> List[Tuple[str, int, str, str]]:
        """
        Check if a line begins with a name.
        :return: List of reports found (type, start position, stub, word or error)
        """
        errors: List[Tuple[str, int, str, str]] = []
        # \b is word boundary. ('\b(^vance|^julian|^clara)\b')
        name_regex = re.compile(r'\b(' + '|'.join(['^' + re.escape(n) for n in self._document.get_names()]) + r')\b',
                                re.IGNORECASE | re.MULTILINE)
        for match in name_regex.finditer(self._plain_text):
            errors.append((Constants.report_name_lines, match.start(), self._find_stub(match.start()), match.group()))
        return errors

    def _check_names(self) -> List[Tuple[str, int, str, str]]:
        """
        Check if all names in text are capitalized.
        :return: List of reports found (type, start position, stub, word or error)
        """
        errors: List[Tuple[str, int, str, str]] = []
        name_regex = re.compile(r'\b(' + '|'.join(map(re.escape, self._document.get_names())) + r')\b')
        for match in name_regex.finditer(self._plain_text):
            errors.append((Constants.report_names_capitalized, match.start(),
                           self._find_stub(match.start()), match.group()))
        return errors

    def _check_leftover(self) -> List[Tuple[str, int, str, str]]:
        """
        Check presence of 'the a' and 'a the' leftovers.
        :return: List of reports found (type, start position, stub, word or error)
        """
        errors: List[Tuple[str, int, str, str]] = []
        for match in Constants.leftover_regex.finditer(self._plain_text):
            errors.append((Constants.report_double_words, match.start(), self._find_stub(match.start()), match.group()))
        return errors

    def _check_repetitions(self) -> List[Tuple[str, int, str, str]]:
        """
        Check if any word is repeated in a row, such as "he did did something".
        :return: List of reports found (type, start position, stub, word or error)
        """
        errors: List[Tuple[str, int, str, str]] = []
        for match in Constants.doubled_words_regex.finditer(self._plain_text):
            errors.append((Constants.report_double_words, match.start(), self._find_stub(match.start()), match.group()))
        return errors

    def _check_similar_words(self) -> List[Tuple[str, int, str, str]]:
        """
        Check for words that are similar but do not trigger spellcheck and usually typed wrong because they are close
        on the keyboard.
        :return: List of reports found (type, start position, stub, word or error)
        """
        errors: List[Tuple[str, int, str, str]] = []
        for match in Constants.similar_words_regex.finditer(self._plain_text):
            word = match.group()
            word_group = Constants.word_to_group[word]
            errors.append((Constants.report_similar, match.start(), self._find_stub(match.start()), str(word_group)))
        return errors
