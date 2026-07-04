class Word:

    def __init__(self, word: str, spans, count: int):
        """
        Container for word data.
        :param word: The word.
        :param spans: All re spans where the word is in text.
        :param count: How many there are.
        """
        self._word = word
        self._spans = spans
        self._count = count
        self._indicator = -1
        self._selected = False

    def set_selected(self, value: bool) -> None:
        """
        Set selected state.
        :param value: True/False
        :return: Noe
        """
        self._selected = value

    def is_selected(self) -> bool:
        """
        Get selected state.
        :return: True/False
        """
        return self._selected

    def get_word(self) -> str:
        """
        Get the word.
        :return: The word as bytes.
        """
        return self._word

    def set_word(self, value: str):
        """
        Set the word.
        :param value: The word as bytes.
        """
        self._word = value

    def get_spans(self):
        """
        Get all re spans where the word is in text.
        :return: The spans.
        """
        return self._spans

    def set_spans(self, value):
        """
        Set the spans.
        :param value: All re spans where the word is in text.
        """
        self._spans = value

    def get_count(self) -> int:
        """
        Get the count of how many times the word appears.
        :return: The count.
        """
        return self._count

    def set_count(self, value: int):
        """
        Set the count of how many times the word appears.
        :param value: The count.
        """
        self._count = value

    def get_indicator(self) -> int:
        """
        Get the indicator value.
        :return: The indicator value.
        """
        return self._indicator

    def has_indicator(self) -> bool:
        """
        Return true if an indicator is set for this word.
        :return: True if an indicator is set for this word.
        """
        if self.get_indicator() > -1:
            return True
        return False

    def set_indicator(self, value: int):
        """
        Set the indicator value.
        :param value: The indicator value.
        """
        self._indicator = value

    def clear_indicator(self) -> None:
        """
        Set indicator to -1.
        :return: None
        """
        self.set_indicator(-1)

    def __str__(self):
        return (f"Word: {self._word}, count: {self._count}, indicator: "
                f"{self._indicator}, selected: {self.is_selected()}")

    # Sorts words by count not by alphabet order.
    def __eq__(self, other):
        if not isinstance(other, Word):
            return NotImplemented
        return self._count == other._count

    def __lt__(self, other):
        if not isinstance(other, Word):
            return NotImplemented
        return self._count < other._count
