import re
from collections import defaultdict
from threading import Thread
from typing import List, Callable, Tuple, Dict

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

    @staticmethod
    def _find_stub(line: str, target: str) -> str:
        """
        Find a part of a line where the supposed problem might be located.
        :param line: Full line of text.
        :param target: String to look for.
        :return: None
        """
        position = line.find(target)
        if position >= 25:
            stub = line[position - 25:position + 25]
        else:
            stub = line[0:position + 25]
        return stub.replace('\n', '')

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

        if self._run_tets:
            # todo the tests are slow on large documents, save ends before tests.
            # todo what is slow in them? Stream error messages into main thread or wait? Can we parallelize with threads?
            check_fails: defaultdict[str, List[Tuple[str, int]]] = defaultdict(list)
            check_functions: List[Callable[[str, int], Tuple[str, List[Tuple[str, int]]]]] = [self._check_leftover,
                                                                                              self._check_repetitions,
                                                                                              self._check_similar_words]
            if self._document.get_names():
                check_functions.append(self._check_names)
                check_functions.append(self._check_name_lines)
            else:
                check_fails[Constants.report_names_capitalized] = [(Strings.report_names_not_configured_lines, -1)]
                check_fails[Constants.report_name_lines] = [(Strings.report_names_not_configured_caps, -1)]

            # Enumerate will not create the whole list in memory.
            for counter, line in enumerate(self._plain_text.splitlines(), start=1):
                for f in check_functions:
                    test_type, test_result = f(line, counter)
                    if test_result:
                        check_fails[test_type].extend(test_result)

            check_fails[Constants.report_close_words].extend(self._check_word_distance())

            wx.CallAfter(self._parent.document_test_callback, check_fails)

    def _check_word_distance(self) -> List[Tuple[str, int]]:
        """
        Check for words with 2 repetitions that are too close together.
        :return: List of errors strings.
        """
        # Recalculate lines by word here to have the freshest data.
        plain_text = self._plain_text.lower().encode('utf-8')
        word_spans = list(Constants.word_matcher.finditer(plain_text))

        # Defaultdict wll create a new empty list if the key does not exist and add it into it. Otherwise, it
        # will just add the word to the existing list under that key.
        lines_by_word: defaultdict[bytes, List[int]] = defaultdict(list)
        line_counter = 1
        for word_span in word_spans:
            word_bytes = word_span.group()
            if word_bytes == b"\n":
                line_counter += 1
            # Dictionary of words as bytes and a list of lines where the word is.
            lines_by_word[word_bytes].append(line_counter)

        errors: List[Tuple[str, int]] = []
        for word, lines in lines_by_word.items():
            if len(lines) == 2:
                # Run this for words with just two repetitions, the rest is visible in the gui coloring tool.
                if (lines[1] - lines[0]) <= self._min_word_distance:
                    errors.append((Strings.report_word_distance.format(word.decode('utf-8'), lines[0], lines[1]),
                                   lines[0]))
        return errors

    def _check_name_lines(self, line: str, line_index: int) -> Tuple[str, List[Tuple[str, int]]]:
        """
        Check if a line begins with a name.
        :param line: Line to check.
        :param line_index: Line number.
        :return: List of errors strings.
        """
        errors: List[Tuple[str, int]] = []
        for name in self._document.get_names():
            if line.lower().startswith(name):
                errors.append((Strings.report_capital_names.format(line_index, name.capitalize(),
                                                                   self._find_stub(line.lower(), name).capitalize()),
                               line_index))
        return Constants.report_name_lines, errors

    def _check_names(self, line: str, line_index: int) -> Tuple[str, List[Tuple[str, int]]]:
        """
        Check if all names in text are capitalized.
        :param line: Line to check.
        :param line_index: Line number.
        :return: List of errors strings.
        """
        errors: List[Tuple[str, int]] = []
        names = self._document.get_names()
        for name in names:
            # Names in names are not capitalized already, so we just look for them.
            if name in line:
                errors.append((Strings.report_names.format(line_index, name, self._find_stub(line, name)), line_index))
        return Constants.report_names_capitalized, errors

    def _check_leftover(self, line: str, line_index: int) -> Tuple[str, List[Tuple[str, int]]]:
        """
        Check presence of 'the a' and 'a the' leftovers.
        :param line: Line to check.
        :param line_index: Line number.
        :return: List of errors strings.
        """
        errors: List[Tuple[str, int]] = []
        variants = (r'\b(?:the a|a the)\b', r' as \w+ a ')
        for regex in variants:
            match = re.search(regex, line)
            if match:
                errors.append((Strings.report_leftover.format(line_index, match.group(),
                                                              self._find_stub(line, match.group())), line_index))
        return Constants.report_leftover, errors

    def _check_repetitions(self, line: str, line_index: int) -> Tuple[str, List[Tuple[str, int]]]:
        """
        Check if any word is repeated in a row, such as "he did did something".
        :param line: Line to check.
        :param line_index: Line number.
        :return: List of errors strings.
        """
        errors: List[Tuple[str, int]] = []
        regex = r'\b(\w+)(?:\s+\1)+\b'
        match = re.search(regex, line)
        if match:
            errors.append((Strings.report_repetition.format(line_index, match.group(),
                                                            self._find_stub(line, match.group())), line_index))
        return Constants.report_repetition, errors

    def _check_similar_words(self, line: str, line_index: int) -> Tuple[str, List[Tuple[str, int]]]:
        """
        Check for words that are similar but do not trigger spellcheck and usually typed wrong because they are close
        on the keyboard.
        :param line: Line to check.
        :param line_index: Line number.
        :return: List of errors strings.
        """
        errors: List[Tuple[str, int]] = []
        word_list = [
            ("shorty", "shortly"),
            ("statue", "statute"),
            ("form", "from"),
            ("plan", "plane"),
            ("unit", "until"),
            ("thought", "though"),
            ("trough", "tough"),
            ("trail", "trial"),
            ("causal", "casual"),
            ("unite", "untie"),
            ("sacred", "scared"),
            ("marital", "martial"),
            ("desert", "dessert"),
            ("principal", "principle"),
            ("complement", "compliment"),
            ("stationery", "stationary"),
            ("affect", "effect"),
            ("moral", "morale"),
            ("human", "humane"),
            ("lose", "loose"),
            ("definitely", "defiantly"),
            ("quiet", "quite"),
            ("diary", "dairy"),
            ("angel", "angle"),
            ("bread", "beard"),
            ("prosecute", "persecute"),
            ("adapt", "adept", "adopt"),
            ("peek", "peak", "pique"),
            ("pore", "pour", "poor"),
            ("discreet", "discrete"),
            ("elicit", "illicit"),
            ("wary", "weary"),
            ("metal", "mettle"),
            ("patients", "patience"),
            ("altar", "alter"),
            ("assent", "ascent"),
            ("bazaar", "bizarre"),
            ("canvas", "canvass"),
            ("capital", "capitol"),
            ("cereal", "serial"),
            ("chord", "cord"),
            ("council", "counsel"),
            ("currant", "current"),
            ("dual", "duel"),
            ("flea", "flee"),
            ("hoard", "horde"),
            ("lightning", "lightening"),
            ("loath", "loathe"),
            ("miner", "minor"),
            ("naval", "navel"),
            ("ordinance", "ordnance"),
            ("pedal", "peddle", "petal"),
            ("profit", "prophet"),
            ("shear", "sheer"),
            ("stair", "stare"),
            ("vial", "vile"),
            ("heard", "hears")
        ]
        for word_group in word_list:
            for word in word_group:
                match = re.search(fr"\b{re.escape(word)}\b", line)
                if match:
                    errors.append((Strings.report_similar.format(line_index, str(word_group),
                                                                 self._find_stub(line, word)), line_index))
        return Constants.report_similar, errors
