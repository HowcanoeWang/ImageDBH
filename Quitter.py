# -*- coding: utf-8 -*-
from tkinter import *
from  tkinter.messagebox import askokcancel

class Quitter(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        widget = Button(self, text='quit', command=self.quit)
        widget.pack(side=LEFT, expand=YES, fill=BOTH)

    def quit(self):
        ans = askokcancel('Verfy exit', "Really quit?")
        if ans:
            Frame.quit(self)

if __name__ == '__main__':
    Quitter().mainloop()