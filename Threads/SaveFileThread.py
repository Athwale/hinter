import re
from collections import defaultdict
from threading import Thread
from typing import List, Callable, Tuple

import wx

from Constants import Strings, Constants
from Containers.Document import Document


class SaveFileThread(Thread):
    """
    Thread for saving the current document to disk.
    """

    def __init__(self, parent, document: Document, converted_text: List, plain_text: str) -> None:
        """
        Thread constructor.
        The editor is disabled during this operation.
        :param parent: The frame that called the thread.
        :param document: The document instance to save.
        :param converted_text: Data prepared for saving.
        :param plain_text: Plain text for additional tests.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._document = document
        # Using the text field here is not thread safe. Gui methods can not be called form background threads safely.
        self._converted_text = converted_text
        self._plain_text = plain_text
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

        check_functions: List[Callable[[str, int, str], Tuple[str, List[str]]]] = [self._check_name_lines,
                                                                                   self._check_names,
                                                                                   self._check_leftover,
                                                                                   self._check_repetitions]
        # Enumerate will not create the whole list in memory.
        # todo use this in more places.
        check_fails: defaultdict[str, List[str]] = defaultdict(list)
        for counter, line in enumerate(self._plain_text.splitlines(), start=1):
            stub = line[0:25] if len(line) >= 25 else line
            for f in check_functions:
                test_type, test_result = f(line, counter, stub)
                if test_result:
                    check_fails[test_type].extend(test_result)

        for t, e in check_fails.items():
            for err in e:
                print(t, err)

    def _check_name_lines(self, line: str, line_index: int, stub: str) -> Tuple[str, List[str]]:
        """
        Check if a line begins with a name.
        :param line: Line to check.
        :param line_index: Line number.
        :param stub: Line stub.
        :return: List of erros strings.
        """
        errors = []
        for name in self._document.get_names():
            if line.lower().startswith(name):
                errors.append(Strings.report_capital_names.format(line_index, name.capitalize(), stub))
        return Constants.report_name_lines, errors

    def _check_names(self, line: str, line_index: int, stub: str) -> Tuple[str, List[str]]:
        """
        Check if all names in text are capitalized.
        :param line: Line to check.
        :param line_index: Line number.
        :param stub: Line stub.
        :return: List of erros strings.
        """
        errors = []
        names = self._document.get_names()
        if not names:
            errors.append(Strings.report_names_not_configured)
        else:
            for name in names:
                # Names in names are not capitalized already, so we just look for them.
                if name in line:
                    errors.append(Strings.report_names.format(line_index, name, stub))
        return Constants.report_names_capitalized, errors

    @staticmethod
    def _check_leftover(line: str, line_index: int, stub: str) -> Tuple[str, List[str]]:
        """
        Check presence of 'the a' and 'a the' leftovers.
        :param line: Line to check.
        :param line_index: Line number.
        :param stub: Line stub.
        :return: List of erros strings.
        """
        errors = []
        variants = (r'\b(?:the a|a the)\b', r' as \w+ a ')
        for regex in variants:
            match = re.search(regex, line)
            if match:
                errors.append(Strings.report_leftover.format(line_index, match.group(), stub))
        return Constants.report_leftover, errors

    @staticmethod
    def _check_repetitions(line: str, line_index: int, stub: str) -> Tuple[str, List[str]]:
        """
        Check if any word is repeated in a row, such as "he did did something".
        :param line: Line to check.
        :param line_index: Line number.
        :param stub: Line stub.
        :return: List of erros strings.
        """
        errors = []
        regex = r'\b(\w+)(?:\s+\1)+\b'
        match = re.search(regex, line)
        if match:
            errors.append(Strings.report_repetition.format(line_index, match.group(), stub))
        return Constants.report_repetition, errors

        # todo - similar words shortly, shorty
        # todo report while running into the main thread?
