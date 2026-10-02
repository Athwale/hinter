import wx.lib.newevent


class Events:
    # Used in Notes Editor dialog to indicate changes to notes which has to make the document modified in main frame.
    TextChangedEvent, EVT_TEXT_CHANGED = wx.lib.newevent.NewCommandEvent()
    # Used in Notes Editor dialog to prevent multiple notes dialog from opening.
    NotesClosedEvent, EVT_NOTES_CLOSED = wx.lib.newevent.NewCommandEvent()
