import wx
import wx.stc as stc

class XmlSTC(stc.StyledTextCtrl):

    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent)

        self.SetLexer(stc.STC_LEX_XML)
        text = "fobj.read()"

        self.SetText(text)


class XmlPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.xml_view = XmlSTC(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.xml_view, 1, wx.EXPAND)
        self.SetSizer(sizer)

class XmlFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='XML View')
        panel = XmlPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = XmlFrame()
    app.MainLoop()