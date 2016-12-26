# -*- coding:UTF-8 -*-
from Quitter import Quitter
from ScrolledCanvas import ScrolledCanvas
from tkinter import *

root = Tk()
root.title('ImageDBH')
ScrolledCanvas.Imagedir = r'D:/OneDrive/Documents/3 UNB/本科毕业设计/Picture/IMG_1559.JPG'
ScrolledCanvas(root).pack(side=TOP)
print(ScrolledCanvas.PointData)
Quitter(root).pack(side=RIGHT,expand=YES,fill=BOTH)
root.mainloop()