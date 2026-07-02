import html
from threading import Thread
from typing import List

import wx
from wx.stc import StyledTextCtrl

from Constants import Constants
from Containers.Document import Document


class SaveFileThread(Thread):
    """
    Thread for saving the current document to disk.
    """

    def __init__(self, parent, document: Document, text_field: StyledTextCtrl) -> None:
        """
        Thread constructor.
        The editor is disabled during this operation.
        :param parent: The frame that called the thread.
        :param document: The document instance to save.
        :param text_field: StyledTextCtrl to convert the document from.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._document = document
        self._main_text_field = text_field
        self.start()

    def run(self) -> None:
        """
        Run the file saving task and post an event back to the main thread.
        :return: None
        """
        self._document.set_converted(self._convert_document())
        try:
            if self._document.save_document():
                wx.CallAfter(self._parent.save_document_callback, True)
            else:
                wx.CallAfter(self._parent.save_document_callback, False)
        except PermissionError as _:
            wx.CallAfter(self._parent.save_document_callback, False)

    def _convert_document(self) -> List:
        """
        Extracts text and styling into the simple dictionary format.
        :return: List of tuples with style and text information.
        """
        converted = []

        length = self._main_text_field.GetTextLength()
        if length == 0:
            return converted

        current_style: int = self._main_text_field.GetStyleAt(0)
        chunk_start: int = 0
        for pos in range(length):
            style_at_pos = self._main_text_field.GetStyleAt(pos)

            # When the style changes, save the previous chunk.
            if style_at_pos != current_style:
                text_chunk = self._main_text_field.GetTextRange(chunk_start, pos)
                # Escape HTML characters (<, >, &, etc.)
                escaped_text = html.escape(text_chunk)

                for style, style_id in Constants.style_map.items():
                    if style_id == current_style:
                        converted.append((style, escaped_text))

                current_style = style_at_pos
                chunk_start = pos
        # Save last chunk where the style does not change.
        text_chunk = self._main_text_field.GetTextRange(chunk_start, length)
        for style, style_id in Constants.style_map.items():
            if style_id == current_style:
                converted.append((style, html.escape(text_chunk)))
        return converted
