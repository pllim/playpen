"""Simple GUI to convert flux to mag and vice versa.

Usage::

    python gui_fluxmag.py

"""
from math import log10, pow
import os

import Image
import ImageTk
import Tkinter
from Tkinter import DISABLED, E, NORMAL, NW, RAISED, RIDGE, W


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'
_LOGOFILE = 'data/logo1.jpg'


class Application(Tkinter.Frame):
    msg_rdy = 'Ready'
    msg_na = 'N/A'
    msg_ferr = 'Invalid flux!'
    msg_merr = 'Invalid mag!'

    # UI initialization
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.grid(padx=5, pady=5)
        self.createWidgets()
        self.master.bind('<Motion>', self.mouseMoveHandler)

    # Convert between fluxes and magnitudes
    def calcFunc(self):
        i = self.radioVar.get()

        # Flux to mag
        if i == 0:
            try:
                v1 = float(self.fluxVar.get())
            except ValueError:
                self.magVar.set(self.msg_na)
                self.msgLabel['fg'] = 'red'
                self.msgVar.set(self.msg_ferr)
            else:
                v2 = -2.5 * log10(v1)
                self.magVar.set(str(v2))
                self.msgLabel['fg'] = 'green'
                self.msgVar.set(self.msg_rdy)

        # Mag to flux
        else:
            try:
                v1 = float(self.magVar.get())
            except ValueError:
                self.fluxVar.set(self.msg_na)
                self.msgLabel['fg'] = 'red'
                self.msgVar.set(self.msg_merr)
            else:
                v2 = pow(10,-0.4*v1)
                self.fluxVar.set(str(v2))
                self.msgLabel['fg'] = 'green'
                self.msgVar.set(self.msg_rdy)

    # Enable/disable text fields
    def greyText(self):
        i = self.radioVar.get()

        # Flux text is active
        if i == 0:
            self.magEntry['state'] = DISABLED
            self.fluxEntry['state'] = NORMAL
            self.fluxEntry.delete(0, len(self.fluxVar.get()))

        # Mag text is active
        else:
            self.fluxEntry['state'] = DISABLED
            self.magEntry['state'] = NORMAL
            self.magEntry.delete(0, len(self.magVar.get()))

    # Mouse motion event handler
    def mouseMoveHandler(self, event):
        self.crdVar.set('{:.0f},{:.0f} ({:.0f},{:.0f})'.format(
            event.x, event.y, event.x_root, event.y_root))

    # UI layout
    def createWidgets(self):
        # Drop down menu with menu options
        self.mainMenu = Tkinter.Menubutton(self, text='File', relief=RAISED)
        self.mainMenu.grid(column=0, row=0, sticky=NW)
        self.mainMenu.subMenu = Tkinter.Menu(self.mainMenu, tearoff=0)
        self.mainMenu['menu'] = self.mainMenu.subMenu
        self.mainMenu.subMenu.insert_command(0, label='Quit', command=self.quit)

        # Logo
        self.logoDisp = Tkinter.Canvas(self, height=100, width=100)
        self.logoDisp.grid(column=0, row=1, columnspan=2)
        self.imtk = ImageTk.PhotoImage(Image.open(_LOGOFILE))
        self.logoDisp.create_image(10, 10, anchor=NW, image=self.imtk)

        # Message display
        self.msgVar = Tkinter.StringVar()
        self.msgVar.set(self.msg_rdy)
        self.msgLabel = Tkinter.Label(self, fg='green', bg='black',
                                      relief=RIDGE, textvariable=self.msgVar)
        self.msgLabel.grid(column=0, row=2, columnspan=2, sticky=E+W)

        # Flux field
        self.fluxVar = Tkinter.StringVar()
        self.fluxLabel = Tkinter.Label(self, text='Flux')
        self.fluxLabel.grid(column=0, row=3, sticky=E)
        self.fluxEntry = Tkinter.Entry(self, bg='white', fg='black',
                                       textvariable=self.fluxVar)
        self.fluxEntry.grid(column=1, row=3, sticky=E+W)

        # Mag field
        self.magVar = Tkinter.StringVar()
        self.magLabel = Tkinter.Label(self, text='Mag')
        self.magLabel.grid(column=0, row=4, sticky=E)
        self.magEntry = Tkinter.Entry(self, bg='white', fg='black',
                                      textvariable=self.magVar)
        self.magEntry.grid(column=1, row=4, sticky=E+W)

        # Radio buttons to choose between flux and mag (flux enabled by default)
        self.radioVar = Tkinter.IntVar()
        self.fluxRadio = Tkinter.Radiobutton(
            self, text='Flux to mag', variable=self.radioVar, value=0,
            command=self.greyText)
        self.fluxRadio.grid(column=0, row=5)
        self.fluxRadio.select()
        self.greyText()
        self.magRadio = Tkinter.Radiobutton(
            self, text='Mag to flux', variable=self.radioVar, value=1,
            command=self.greyText)
        self.magRadio.grid(column=1, row=5)
        self.magRadio.deselect()

        # Calculation button
        self.calcButton = Tkinter.Button(self, text='Calculate', fg='red',
                                         command=self.calcFunc)
        self.calcButton.grid(column=0, row=6, columnspan=2, sticky=E+W)

        # Mouse coord display
        self.crdVar = Tkinter.StringVar()
        self.crdLabel = Tkinter.Label(self, textvariable=self.crdVar)
        self.crdLabel.grid(column=1, row=10, sticky=E)


# Run the application
root = Tkinter.Tk()
app = Application(master=root)
app.master.title('Of Fluxes And Magnitudes')
app.mainloop()
