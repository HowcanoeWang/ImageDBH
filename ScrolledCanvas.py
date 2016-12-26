from tkinter import *
from tkinter.messagebox import *
from PIL import ImageTk
from pandas import *
pandas.options.mode.chained_assignment = None  # close warning

class ScrolledCanvas(Frame):
    Imagedir = r'D:\OneDrive\Program\Python\UNB\IMG_1545.JPG'
    NewTree_OnOff = -1
    TreeNum = 0
    PointData = DataFrame(columns=('UP','UC','UL','DP','DC','DL','DBH'))
    PointData.index.name='TreeID'
    '''DataFrame
    TreeID UP(Up points)               UC(Up centre) UL(Up line) DP(Down points)             DC(Down centre) DL(Down line) DBH
    0      [(Ux1,Uy1,id),(Ux2,Uy2,id)] [(Ucx,Ucy)]   3           [(Dx1,Dy1,id),(Dx2,Dy2,id)] [(Dcx,Dcy) ]    4             18.7
    '''
    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        self.pack(expand=YES,fill=BOTH)

        # make menu
        menubar = Frame(self)
        menubar.config(bg='white')
        menubar.pack(side=TOP, fill=X)

        fbutton = Menubutton(menubar,text='File',underline=0)
        fbutton.pack(side=LEFT)
        file = Menu(fbutton,tearoff=False)
        file.add_command(label='New',command=self.notdone, underline=0)
        file.add_command(label='Open',command=self.notdone, underline=1)
        fbutton.config(menu=file,bg='white')

        ebutton = Menubutton(menubar, text='Edit',underline=0)
        ebutton.pack(side=LEFT)
        edit = Menu(ebutton,tearoff=False)
        edit.add_command(label='Add points',command=self.Add_points_on, underline=0)
        edit.add_command(label='Move points',command=self.notdone,underline=0)
        edit.add_command(label='Delete points',command=self.notdone,underline=0)
        ebutton.config(menu=edit,bg='white')

        canv = Canvas(self, relief=SUNKEN)
        canv.config(width=800, height=600)
        canv.config(highlightthickness=0)

        sbarx = Scrollbar(self,orient='horizontal')
        sbary = Scrollbar(self)
        sbarx.config(command=canv.xview,bg='white')
        sbary.config(command=canv.yview,bg='white')
        canv.config(xscrollcommand=sbarx.set)
        canv.config(yscrollcommand=sbary.set)

        sbary.pack(side=RIGHT, fill=Y)
        canv.pack(side=TOP, expand=YES,fill=BOTH)
        sbarx.pack(side=TOP, fill=X)

        self.OpenPicture(canv)
        # canv.bind('<Double-1>',self.onDoubleClick)
        canv.bind('<ButtonPress-1>', self.onSingleClick)

        self.canvas = canv

    def notdone(self):
        showerror('Not implemented','Not yet available')

    def OpenPicture(self,canv):
        photo = ImageTk.PhotoImage(file=self.Imagedir)
        self.photo = photo
        canv.create_image(0, 0, image=photo, anchor=NW)
        canv.config(scrollregion=(0,0,photo.width(),photo.height()))

    def Add_points_on(self):
        self.NewTree_OnOff=0

    def onSingleClick(self,event):
        x=self.canvas.canvasx(event.x);y=self.canvas.canvasy(event.y)
        i=self.TreeNum
        # if it is the first click -> Up point 1
        if self.NewTree_OnOff == 0:
            # Draw points
            ID = self.Draw_Point(x, y, 'blue')
            # Add a new row
            self.PointData.loc[i] = {'UP': [], 'UC': [],'UL':0, 'DP': [], 'DC': [], 'DL':0,'DBH': 0}
            # Add information to DataFrame
            self.PointData.UP[i].append((x, y, ID))
            # Fresh OnOff index
            self.NewTree_OnOff = 1
        # if it is the second click -> Up point 2
        elif self.NewTree_OnOff == 1:
            # Draw points
            ID_p = self.Draw_Point(x, y, 'blue')
            # Add information to DataFrame
            self.PointData.UP[i].append((x, y, ID_p))
            # Calculate centre point
            (Cx, Cy)=self.Calcu_CentrePoints(self.PointData.UP[i])
            # Draw centre point
            ID_c = self.Draw_Point(Cx, Cy, 'green')
            # Add centre point information to DataFrame
            self.PointData.UC[i].append((Cx, Cy, ID_c))
            # Draw curve line
            ID_l = self.Draw_Curveline(self.PointData.UP[i],self.PointData.UC[i])
            # Add line information to DataFrame
            self.PointData.UL[i] = ID_l
            # Fresh OnOff index
            self.NewTree_OnOff = 2
        # if it is the tird click -> Down point 1
        elif self.NewTree_OnOff == 2:
            # Draw points
            ID = self.Draw_Point(x, y, 'red')
            # Add information to DataFrame
            self.PointData.DP[i].append((x, y, ID))
            # Fresh OnOff index
            self.NewTree_OnOff = 3
        # if it is the forth click -> Down point2
        elif self.NewTree_OnOff == 3:
            # Draw points
            ID_p = self.Draw_Point(x, y, 'red')
            # Add information to DataFrame
            self.PointData.DP[i].append((x, y, ID_p))
            # Calculate centre point
            (Cx, Cy) = self.Calcu_CentrePoints(self.PointData.DP[i])
            # Draw centre point
            ID_c = self.Draw_Point(Cx, Cy, 'green')
            # Add centre point information to DataFrame
            self.PointData.DC[i].append((Cx, Cy, ID_c))
            # Draw curve line
            ID_l = self.Draw_Curveline(self.PointData.DP[i], self.PointData.DC[i])
            # Add line information to DataFrame
            self.PointData.DL[i] = ID_l
            # Fresh OnOff index
            self.NewTree_OnOff = -1
            # Add tree Number
            self.TreeNum += 1
        # print(self.PointData)

    def Draw_Curveline(self,UP_DP,UC_DC):
        '''
        # create_line has three points to draw curve line
        # but if these three points is P_baseL, P_baseR, and P_top
        # the curve line would scross P_centre rather than P_top
        # So we need to calculate P_top if we want the curve line across P_centre
        # (P)_baseL--------(P)_baseR
        #   \             /
        #    \   (P)_c  /
        #     \       /
        #     (P)_top
        '''
        Xbl = UP_DP[0][0]
        Ybl = UP_DP[0][1]
        Xbr = UP_DP[1][0]
        Ybr = UP_DP[1][1]
        Xc  = UC_DC[0][0]
        Yc  = UC_DC[0][1]
        Xtop = 2 * Xc - (Xbl + Xbr) / 2
        Ytop = 2 * Yc - (Ybl + Ybr) / 2
        ObjectID = self.canvas.create_line((Xbl, Ybl), (Xtop, Ytop), (Xbr, Ybr), smooth=True, fill="pink")
        return ObjectID

    def Draw_Point(self,x,y,color):
        ObjectID = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline=color)
        return ObjectID

    def Calcu_CentrePoints(self,CentrePoints):
        x1=CentrePoints[0][0]
        y1=CentrePoints[0][1]
        x2=CentrePoints[1][0]
        y2=CentrePoints[1][1]
        Cx=(x1+x2)/2
        Cy=(y1+y2)/2
        return Cx,Cy

if __name__ == '__main__':
    ScrolledCanvas().mainloop()