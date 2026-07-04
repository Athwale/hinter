from threading import Thread
from typing import List

import wx

from Containers.Document import Document


class SaveFileThread(Thread):
    """
    Thread for saving the current document to disk.
    """

    def __init__(self, parent, document: Document, converted_text: List) -> None:
        """
        Thread constructor.
        The editor is disabled during this operation.
        :param parent: The frame that called the thread.
        :param document: The document instance to save.
        :param converted_text: Data prepared for saving.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._document = document
        # Using the text field here is not thread safe. Gui methods can not be called form background threads safely.
        self._converted_text = converted_text
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
