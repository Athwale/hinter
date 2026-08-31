import wx.lib.newevent


class Events:
    TextChangedEvent, EVT_TEXT_CHANGED = wx.lib.newevent.NewCommandEvent()
    NotesClosedEvent, EVT_NOTES_CLOSED = wx.lib.newevent.NewCommandEvent()
