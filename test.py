import wx
import wx.stc as stc

class XmlSTC(stc.StyledTextCtrl):

    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent)

        self.SetLexer(stc.STC_LEX_XML)
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "size:10,face:Courier New")
        faces = { 'mono' : 'Courier New',
                  'helv' : 'Arial',
                  'size' : 10,
                  }

        # XML styles
        # Default
        self.StyleSetSpec(stc.STC_H_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)

        # Number
        self.StyleSetSpec(stc.STC_H_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # Tag
        self.StyleSetSpec(stc.STC_H_TAG, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Value
        self.StyleSetSpec(stc.STC_H_VALUE, "fore:#7F0000,size:%(size)d" % faces)

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