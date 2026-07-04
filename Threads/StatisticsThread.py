from threading import Thread

import wx


class StatisticsThread(Thread):
    """
    Text statistics thread
    """

    def __init__(self, parent, text: str) -> None:
        """
        Text statistics thread constructor.
        :param parent: The frame that called the thread.
        :param text: Plain text to run on.
        """
        super().__init__(daemon=True)
        self._text = text
        self._parent = parent

    def run(self) -> None:
        """
        Count various statistics on text and send them back to the main thread.
        :return: None
        """
        wx.CallAfter(self._parent.text_statistics_callback, len(self._text.split()))
