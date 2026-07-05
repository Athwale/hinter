import re
from collections import defaultdict
from threading import Thread
from typing import Dict, List

import wx

from Containers.Document import Document


class ColoratorThread(Thread):
    """
    Thread for calculating word marking data.
    """

    def __init__(self, parent, document: Document, plain_text: str) -> None:
        """
        Thread constructor.
        :param parent: The Frame that called the thread.
        :param document: The document instance to save.
        :param plain_text: Data prepared for saving.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._document = document
        self._text = plain_text
        self._word_matcher = re.compile(rb"\b([A-Za-z0-9]+)\b")
        self.start()

    def run(self) -> None:
        """
        Run the time-consuming calculations.
        Split text into words and prepare word panels containing data about every unique word.
        :return: None
        """
        # This returns a reference and is changed in place, so I do not need to set it back.
        word_data = self._document.get_word_marking_data()
        plain_text = self._text.lower()
        word_spans = list(self._word_matcher.finditer(plain_text.encode('utf-8')))

        # Defaultdict wll create a new empty list if the key does not exist and add it into it. Otherwise, it
        # will just add the word.
        spans_by_word: defaultdict[bytes, List[re.Match]] = defaultdict(list)
        for span in word_spans:
            word_bytes = span.group()
            spans_by_word[word_bytes].append(span)

        plain_words: Dict[bytes, int] = {word: len(spans) for word, spans in spans_by_word.items()}

        # Remove words no longer present.
        if len(plain_words) != len(word_data):
            words_to_remove = [w for w in word_data if w not in plain_words]
            for w in words_to_remove:
                word_data.pop(w)

        wx.CallAfter(self._parent.apply_indicators_callback, plain_words, spans_by_word)
