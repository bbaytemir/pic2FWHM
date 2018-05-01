import wx
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import math
from scipy.stats import norm
from numpy import trapz


class MyCanvas(wx.ScrolledWindow):
    clicks = [[0, 0], [0, 0]]
    point = 0
    bmp = []
    all_datas = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 9 lp/mm 2 key : h(1)-v(0)

    def clear_draw(self):
        self.image = wx.Image(filepath)
        self.w = self.image.GetWidth()
        self.h = self.image.GetHeight()
        self.bmp = wx.Bitmap(self.image)
        self.arr = np.frombuffer(self.image.GetDataBuffer(), dtype='uint8')
        self.arr2 = np.reshape(self.arr, (self.h, self.w, 3))

        self.SetVirtualSize((self.w, self.h))
        self.SetScrollRate(20, 20)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))

        self.buffer = wx.Bitmap(self.w, self.h)
        self.dc = wx.BufferedDC(None, self.buffer)
        self.dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        self.dc.Clear()
        self.DoDrawing(self.dc)

    def __init__(self, parent, id=-1, size=wx.DefaultSize, filepath=None):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.clear_draw()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_RIGHT_UP, self.OnClickRight)
        self.Bind(wx.EVT_KEY_UP, self.DrawGrapha)

    def plot(self, vals, t):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        line, = ax.plot([asd / 13 for asd in t], vals, lw=2)

        poi = vals.index(max(vals))
        pom = vals.index(min(vals))
        spp = vals[poi] - vals[pom]

        print("max @ " + str(t[poi]) + " and value is " + str(vals[poi]))
        print("min @ " + str(t[pom]) + " and value is " + str(vals[pom]))

        ax.annotate('max val: ' + str(vals[poi]), xy=(t[poi] / 13, vals[poi]),
                    xytext=(t[poi] / 13 + 0.1, vals[poi] + 1.3),
                    arrowprops=dict(facecolor='red', shrink=0.05))
        ax.annotate('min val: ' + str(vals[pom]), xy=(t[pom] / 13, vals[pom]),
                    xytext=(t[pom] / 13 - 0.1, vals[pom] - 1.3),
                    arrowprops=dict(facecolor='red', shrink=0.05))

        print("Spp  -> ", spp)

        self.all_datas[self.key][self.data_index] = spp

        plt.show()

    def result_plot(self):
        print(self.all_datas)

        fdv = self.all_datas[0]
        fdh = self.all_datas[1]
        fdvm = max(fdv)
        fdhm = max(fdh)
        fdv = [xa / fdvm for xa in fdv]
        fdh = [xa / fdhm for xa in fdh]

        fig = plt.figure()
        plt.title("Vertical Spp")
        ax = fig.add_subplot(111)
        t = [0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2, 2.5, 3.0]
        line, = ax.plot(t, fdv, lw=2)
        plt.show()
        area_vertical = trapz(fdv, t)
        print("Vertical Noise Equivalent Bandwidth", str(area_vertical))

        fig = plt.figure()
        plt.title("Horizontal Spp")
        ax = fig.add_subplot(111)
        line, = ax.plot(t, fdh, lw=2)
        plt.show()

        area_horizontal = trapz(fdh, t)
        print("Horizontal Noise Equivalent Bandwidth", str(area_horizontal))


    def sigma2Gamma(self, sigma):
        '''Function to convert standard deviation (sigma) to FWHM (Gamma)'''
        return sigma * math.sqrt(2 * math.log(2)) * 2 / math.sqrt(2)

    def Gamma2sigma(self, Gamma):
        '''Function to convert FWHM (Gamma) to standard deviation (sigma)'''
        return Gamma * math.sqrt(2) / (math.sqrt(2 * math.log(2)) * 2)

    def Gaussian(self, k, ro, n_2):
        return (1 / (math.sqrt(2 * math.pow(ro, 2) ** math.pi))) * np.exp(
            -(np.power((k - n_2), 2.) / (math.pow(ro, 2) * 2)))

    key = -1
    data_index = 0

    def DrawGrapha(self, event):
        char = event.GetKeyCode()
        self.key = -1
        if char == 13:  # vertical
            self.dc.Clear()
            self.clear_draw()
            self.Refresh()
            asd = [int(sum(i) / 3) for i in self.arr2[self.clicks[0][1]:self.clicks[1][1],
                                            self.clicks[0][0]]]
            print(asd)
            xx = range(self.clicks[0][1], self.clicks[1][1])
            self.key = 0
            self.plot(asd, xx)
        elif char == 27:
            exit(1)
        elif char == 44:  # horizontal
            self.dc.Clear()
            self.clear_draw()
            self.Refresh()
            asd = [int(sum(i) / 3) for i in self.arr2[self.clicks[0][1], self.clicks[0][0]:self.clicks[1][0]]]
            print(asd)
            xx = range(self.clicks[0][0], self.clicks[1][0])
            self.key = 1
            self.plot(asd, xx)
        elif 48 < char < 58:
            self.data_index = char - 49
        elif char == 82:
            self.result_plot()
        else:
            print(char)
            print("unknown char")

    def OnClick(self, event):
        pos = self.CalcUnscrolledPosition(event.GetPosition())

        self.clicks[0][0] = pos.x
        self.clicks[0][1] = pos.y

        print('point 0 : %d, %d' % (pos.x, pos.y))

    def OnClickRight(self, event):
        pos = self.CalcUnscrolledPosition(event.GetPosition())

        self.clicks[1][0] = pos.x
        self.clicks[1][1] = pos.y

        print('point 1 : %d, %d' % (pos.x, pos.y))

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        'dc = wx.PaintDC(self)'
        dc.SetPen(wx.Pen(wx.RED, 4))
        if self.key == 0:
            dc.DrawLine(self.clicks[0][0], self.clicks[0][1], self.clicks[0][0], self.clicks[1][1])
        elif self.key == 1:
            dc.DrawLine(self.clicks[0][0], self.clicks[0][1], self.clicks[1][0], self.clicks[0][1])

    def DoDrawing(self, dc):
        dc.DrawBitmap(self.bmp, 0, 0)


class MyFrame(wx.Frame):
    def __init__(self, parent=None, id=-1, filepath=None):
        wx.Frame.__init__(self, parent, id, title=filepath)
        self.canvas = MyCanvas(self, -1, filepath=filepath)

        self.canvas.SetMinSize((self.canvas.w, self.canvas.h))
        self.canvas.SetMaxSize((self.canvas.w, self.canvas.h))
        self.canvas.SetBackgroundColour(wx.Colour(0, 0, 0))
        vert = wx.BoxSizer(wx.VERTICAL)
        horz = wx.BoxSizer(wx.HORIZONTAL)
        vert.Add(horz, 0, wx.EXPAND, 0)
        vert.Add(self.canvas, 1, wx.EXPAND, 0)
        self.SetSizer(vert)
        vert.Fit(self)
        self.Layout()


if __name__ == '__main__':
    app = wx.App()
    app.SetOutputWindowAttributes(title='stdout')
    wx.InitAllImageHandlers()

    filepath = 'mtf.jpg'
    if filepath:
        print(filepath)
        myframe = MyFrame(filepath=filepath)
        myframe.Center()
        myframe.Show()
        app.MainLoop()
