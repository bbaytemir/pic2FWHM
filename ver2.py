import wx
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import math
from scipy.stats import norm


class MyCanvas(wx.ScrolledWindow):
    clicks = [[0, 0], [0, 0]]
    point = 0
    bmp = []

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

        line, = ax.plot(t, vals, lw=2)
        dvider = 1
        max_points = argrelextrema(np.array(vals), np.greater)
        print(max_points[0])
        for poi in max_points[0]:
            if vals[poi] > 100:
                print("max @ " + str(t[poi]) + " and value is " + str(vals[poi]))

                sigma = 1 / (vals[poi] * math.sqrt(math.pi * 2))
                fwhm = sigma * 2.3548

                if self.npix != 0:
                    dvider = self.npix
                ax.annotate(
                    'peak : ' + str(vals[poi]) + "\n sigma : " + str(round(sigma, 5)) + "\n fwhm : " + str(round(fwhm, 5)),
                    xy=(t[poi], vals[poi]), xytext=(t[poi] + 3/dvider, vals[poi] + 4/dvider),
                    arrowprops=dict(facecolor='blue', shrink=0.05))

                print("peak  -> ", vals[poi])
                print("sigma -> ", round(sigma, 5))
                print("fwhm  -> ", round(fwhm, 5))

        plt.show()

    npix = 0

    def sigma2Gamma(self, sigma):
        '''Function to convert standard deviation (sigma) to FWHM (Gamma)'''
        return sigma * math.sqrt(2 * math.log(2)) * 2 / math.sqrt(2)

    def Gamma2sigma(self, Gamma):
        '''Function to convert FWHM (Gamma) to standard deviation (sigma)'''
        return Gamma * math.sqrt(2) / (math.sqrt(2 * math.log(2)) * 2)

    def Gaussian(self, k, ro, n_2):
        return (1 / (math.sqrt(2 * math.pow(ro, 2) ** math.pi))) * np.exp(
            -(np.power((k - n_2), 2.) / (math.pow(ro, 2) * 2)))

    def DrawGrapha(self, event):
        char = event.GetKeyCode()
        if char == 13:
            self.dc.Clear()
            self.clear_draw()
            self.Refresh()
            asd = [int(sum(i) / 3) for i in self.arr2[self.clicks[0][1],
                                            self.clicks[0][0]:self.clicks[1][0]]]
            print(asd)
            xx = range(self.clicks[0][0], self.clicks[1][0])
            if self.npix != 0:
                xx = [x / self.npix for x in xx]

            self.plot(asd, xx)
        elif char == 27:
            exit(1)
        elif char == 44:
            self.npix = int(str(input("Please insert a ratio of pix/mm : ")))

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

    filepath = 'ftfa.jpg'
    if filepath:
        print(filepath)
        myframe = MyFrame(filepath=filepath)
        myframe.Center()
        myframe.Show()
        app.MainLoop()
