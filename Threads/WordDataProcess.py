import multiprocessing
import re
from collections import defaultdict
from typing import Dict, List

from Constants import Constants


class WordDataProcess(multiprocessing.Process):
    """
    Thread for calculating word marking data.
    """

    def __init__(self, list_words: List[bytes], plain_text: str, queue: multiprocessing.SimpleQueue) -> None:
        """
        Process constructor.
        :param list_words: The document instance to save.
        :param plain_text: Data prepared for saving.
        :param queue: The Frame that called the thread.
        :return: None
        """
        super().__init__()
        self._list_words = list_words
        self._text = plain_text
        self._queue = queue
        self.start()

    def run(self) -> None:
        """
        Run the time-consuming calculations.
        Split text into words and prepare word panels containing data about every unique word.
        :return: None
        """
        # This returns a reference and is changed in place, so we do not need to set it back.
        plain_text: bytes = self._text.lower().encode('utf-8')
        word_spans: List[re.Match] = list(Constants.word_matcher.finditer(plain_text))

        # Defaultdict wll create a new empty list if the key does not exist and add it into it. Otherwise, it
        # will just add the word to the existing list under that key.
        spans_by_word: defaultdict[bytes, list[tuple[int, int]]] = defaultdict(list)
        lines_by_word: defaultdict[bytes, List[int]] = defaultdict(list)
        line_counter = 1
        for word_span in word_spans:
            word_bytes = word_span.group()
            if word_bytes == b"\n":
                line_counter += 1
                continue
            # Dictionary of words as bytes and a list of regex matches where the word is.
            spans_by_word[word_bytes].append(word_span.span())

            # Dictionary of words as bytes and a list of lines where the word is.
            lines_by_word[word_bytes].append(line_counter)

        # Dictionary of words as bytes and the amount of each word.
        plain_words: Dict[bytes, int] = {word: len(spans) for word, spans in spans_by_word.items()}

        # Remove words no longer present.
        if len(plain_words) != len(self._list_words):
            words_to_remove = [w for w in self._list_words if w not in plain_words]
            for w in words_to_remove:
                self._list_words.remove(w)

        self._queue.put((Constants.process_id_data, (plain_words, spans_by_word, lines_by_word, self._list_words)))
