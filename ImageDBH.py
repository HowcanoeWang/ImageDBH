# -*- coding:UTF-8 -*-
from tkinter import *
from tkinter.messagebox import *
from PIL import ImageTk,Image

class ScrolledCanvas(Frame):
    Imagedir = r'D:\OneDrive\Program\Python\UNB\IMG_1545.JPG'
    NewTree_OnOff = -1
    TreeNum = 0
    PointNum = {'UP1': [],'UP2':[], 'UC': [],'UL':[], 'DP1': [],'DP2':[], 'DC': [], 'DL':[],'DBH': [],'Comb':[]}
    PhotoSize = []
    Rotate = 0 # []+(逆时针90度), -(顺时针90度)
    '''DataFrame
    Not need to record the position because can get the point position by :canvas.coords(ID)
    coords(i, new_xy) # change coordinates
    TreeID            [0, 1, 2, 3, 4, 5...]
    UP1 (Up Point1)   [2,10,...]
    UP2 (Up Point2)   [3,11,...]
    UC  (UP Centre)   [4,12,...]
    UL  (Up Line)     [5,13,...]
    DP1 (Down Point1) [6,14,...]
    DP2 (Down Point2) [7,15,...]
    DC  (Down Cnetre) [8,16,...]
    DL  (Down Line)   [9,17,...]
    DBH (Diametre)    [19.07,]
    Comb[0 [[UP1,UP2,UC] -> UL,[DP1,DP2,UC] -> DL],
         1 [[UL]              ,[DL]              ],
         2 [[]                ,[]                ],...]
    '''
    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        self.pack(expand=YES,fill=BOTH)

        canvas = Canvas(self, relief=SUNKEN)
        canvas.config(width=800, height=600)
        canvas.config(highlightthickness=0)
        canvas.bind('<ButtonPress-1>', self.onPutPoint)
        canvas.bind('<B1-Motion>',self.onMovePoint)
        canvas.bind('<Double-1>', self.Num2Position)
        canvas.bind('<Double-2>', self.Open_Picture)
        canvas.bind('<Double-3>',self.ClearCanvas)

        sbarx = Scrollbar(self,orient='horizontal')
        sbary = Scrollbar(self)
        sbarx.config(command=canvas.xview,bg='white')
        sbary.config(command=canvas.yview,bg='white')
        canvas.config(xscrollcommand=sbarx.set)
        canvas.config(yscrollcommand=sbary.set)

        sbary.pack(side=RIGHT, fill=Y)
        sbarx.pack(side=BOTTOM, fill=X)
        canvas.pack(side=TOP, expand=YES,fill=BOTH)

        self.canvas = canvas
        # self.Open_Picture()

    def Open_Picture(self,event=None):
        self.ClearCanvas()
        image = Image.open(self.Imagedir)
        # self.kinds = [file=image, image.transpose]
        # photo = ImageTk.PhotoImage(file=self.Imagedir)
        if self.Rotate == 90 or self.Rotate == -270:
            photo = ImageTk.PhotoImage(image.transpose(Image.ROTATE_270))
        elif self.Rotate == 180 or self.Rotate == -180:
            photo = ImageTk.PhotoImage(image.transpose(Image.ROTATE_180))
        elif self.Rotate == 270 or self.Rotate == -90:
            photo = ImageTk.PhotoImage(image.transpose(Image.ROTATE_90))
        else:
            photo = ImageTk.PhotoImage(image)
        self.photo = photo
        self.canvas.create_image(0, 0, image=photo, anchor=NW)
        self.canvas.config(scrollregion=(0,0,photo.width(),photo.height()))
        self.PhotoSize=[photo.width(),photo.height()]

    def ClearCanvas(self,event=None):
        # event.widget.delete('all')  # use tag all
        self.canvas.delete('all')
        self.PointNum = {'UP1': [],'UP2':[], 'UC': [],'UL':[], 'DP1': [],'DP2':[], 'DC': [], 'DL':[],'DBH': [],'Comb':[]}
        self.TreeNum = 0

    def onPutPoint(self,event):
        if len(self.canvas.find_all()) > 0:
            x=self.canvas.canvasx(event.x);y=self.canvas.canvasy(event.y)
            i=self.TreeNum
            # if it is the first click -> Up point 1
            if self.NewTree_OnOff == 0:
                # Draw points
                ID_p1 = self.Create_Point(x, y, 'blue')
                # Add information to DataFrame
                self.PointNum['UP1'].append(ID_p1)
                self.PointNum['DBH'].append(0)
                self.PointNum['Comb'].append([])
                # Fresh OnOff index
                self.NewTree_OnOff = 1
            # if it is the second click -> Up point 2
            elif self.NewTree_OnOff == 1:
                # Draw points
                ID_p2 = self.Create_Point(x, y, 'blue')
                # Add information to DataFrame
                self.PointNum['UP2'].append(ID_p2)
                # Calculate centre point
                (Cx, Cy)=self.Calcu_CentrePoints(self.PointNum['UP1'][i],self.PointNum['UP2'][i])
                # Draw centre point
                ID_c = self.Create_Point(Cx, Cy, 'green')
                # Add centre point information to DataFrame
                self.PointNum['UC'].append(ID_c)
                # Add curve line comb
                self.PointNum['Comb'][i].append([self.PointNum['UP1'][i], self.PointNum['UP2'][i], self.PointNum['UC'][i]])
                # Draw curve line
                ID_l = self.Create_Curveline(self.PointNum['Comb'][i][0])
                # Add line information to DataFrame
                self.PointNum['UL'].append(ID_l)
                # Fresh OnOff index
                self.NewTree_OnOff = 2
            # if it is the tird click -> Down point 1
            elif self.NewTree_OnOff == 2:
                # Draw points
                ID_p1 = self.Create_Point(x, y, 'red')
                # Add information to DataFrame
                self.PointNum['DP1'].append(ID_p1)
                # Fresh OnOff index
                self.NewTree_OnOff = 3
            # if it is the forth click -> Down point2
            elif self.NewTree_OnOff == 3:
                # Draw points
                ID_p2 = self.Create_Point(x, y, 'red')
                # Add information to DataFrame
                self.PointNum['DP2'].append(ID_p2)
                # Calculate centre point
                (Cx, Cy) = self.Calcu_CentrePoints(self.PointNum['DP1'][i],self.PointNum['DP2'][i])
                # Draw centre point
                ID_c = self.Create_Point(Cx, Cy, 'green')
                # Add centre point information to DataFrame
                self.PointNum['DC'].append(ID_c)
                # Add curve line comb
                self.PointNum['Comb'][i].append([self.PointNum['DP1'][i], self.PointNum['DP2'][i], self.PointNum['DC'][i]])
                # Draw curve line
                ID_l = self.Create_Curveline(self.PointNum['Comb'][i][1])
                # Add line information to DataFrame
                self.PointNum['DL'].append(ID_l)
                # Fresh OnOff index
                self.NewTree_OnOff = -1
                # Add tree Number
                self.TreeNum += 1
                print(self.PointNum)
            if not self.NewTree_OnOff == -1:
                print(self.PointNum)

    def onMovePoint(self,event):
        if self.NewTree_OnOff == -1:# not in add point mode
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            IDtouched = event.widget.find_closest(x,y)
            if len(IDtouched)==1 and self.isin(IDtouched[0]):
                self.canvas.coords(IDtouched, (x-5,y-5,x+5,y+5))
                Comb = self.PointNum['Comb']
                for i in range(len(Comb)):
                    if IDtouched[0] in Comb[i][0]: # move points of up points
                        lineID = self.PointNum['UL'][i]
                        # move line
                        self.Create_Curveline(self.PointNum['Comb'][i][0],lineID)
                    if IDtouched[0] in Comb[i][1]: # move points of down points
                        lineID = self.PointNum['DL'][i]
                        # move line
                        self.Create_Curveline(self.PointNum['Comb'][i][1],lineID)

    def Create_Curveline(self,ID,lineID=None):
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
        ID_1=ID[0];ID_2=ID[1];ID_C=ID[2]
        P1 = self.ID2Position(ID_1)
        P2 = self.ID2Position(ID_2)
        Pc = self.ID2Position(ID_C)
        # coords(i, new_xy)
        Xbl = P1[0]
        Ybl = P1[1]
        Xc = Pc[0]
        Yc = Pc[1]
        Xbr = P2[0]
        Ybr = P2[1]
        Xtop = 2 * Xc - (Xbl + Xbr) / 2
        Ytop = 2 * Yc - (Ybl + Ybr) / 2
        if lineID == None:
            ObjectID = self.canvas.create_line((Xbl, Ybl), (Xtop, Ytop), (Xbr, Ybr), smooth=True, fill="pink")
            return ObjectID
        else:
            self.canvas.coords(lineID,[Xbl, Ybl, Xtop, Ytop, Xbr, Ybr])

    def Create_Point(self,x,y,color):
        ObjectID = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline=color)
        return ObjectID

    def Calcu_CentrePoints(self,ID1,ID2):
        P1 = self.ID2Position(ID1)
        P2 = self.ID2Position(ID2)
        x1=P1[0]
        y1=P1[1]
        x2=P2[0]
        y2=P2[1]
        Cx=(x1+x2)/2
        Cy=(y1+y2)/2
        return Cx,Cy

    def ID2Position(self,ID):
        Position = self.canvas.coords(ID)
        if len(Position) == 4: # curve line returns 6 parametres while points(circle) returns 4 parametres
            X_5 = Position[0]
            Y_5 = Position[1]
            Position = [X_5+5,Y_5+5]
        return Position

    def isin(self,ID):
        isin = False
        for i in ['UP1','UP2', 'UC', 'DP1','DP2', 'DC', 'DL']:
            Ans = ID in self.PointNum[i]
            if Ans or False:
                isin = True
        return isin

    def Num2Position(self,event=None):
        # UP1 | UP2 | UC | DP1 | DP2 | DC | PhotoSize + PhotoInfo
        from PIL import Image, ExifTags
        img = Image.open(self.Imagedir)
        exif_human = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        # XResolution = exif_human['XResolution'][0]
        # YResolution = exif_human['YResolution'][0]
        if exif_human['FocalLength'][1]==0: # lack data
            FocalLength = 0
        else:
            FocalLength = exif_human['FocalLength'][0]/exif_human['FocalLength'][1] # mm
        if exif_human['FocalPlaneResolutionUnit'] == 2: # inch(default)
            FPX = exif_human['FocalPlaneXResolution'][1] * 2.54/100 # mm
            FPY = exif_human['FocalPlaneYResolution'][1] * 2.54/100 # mm
        else:
            FPX = str(exif_human['FocalPlaneXResolution'][1])+'mm'
            FPY = str(exif_human['FocalPlaneYResolution'][1])+'mm'
        info = {'Size': img.size,
                # 'YResolution': YResolution,
                # 'XResolution': XResolution,
                'FocalLength': FocalLength,
                'FPX':FPX,
                'FPY':FPY,
                'Model': exif_human['Model'],
                }
        print(info)
        PointPosition = []
        for i in range(len(self.PointNum['DC'])):
            PointPosition.append([self.ID2Position(self.PointNum['UP1'][i]),
                                  self.ID2Position(self.PointNum['UP2'][i]),
                                  self.ID2Position(self.PointNum['UC'][i]),
                                  self.ID2Position(self.PointNum['DP1'][i]),
                                  self.ID2Position(self.PointNum['DP2'][i]),
                                  self.ID2Position(self.PointNum['DC'][i]),
                                  self.PhotoSize,
                                  info])
        print(PointPosition)
        return PointPosition

class MenuBar(Frame):

    def __init__(self,parent=None):
        Frame.__init__(self, parent)
        self.pack()
        menubar = Frame(self)
        menubar.config(bg='white')
        menubar.pack(side=TOP, fill=X)

        fbutton = Menubutton(menubar, text='File', underline=0)
        fbutton.pack(side=LEFT)
        file = Menu(fbutton, tearoff=False)
        file.add_command(label='New', command=self.notdone, underline=0)
        file.add_command(label='Open', command=self.notdone, underline=1)
        fbutton.config(menu=file, bg='white')

        ebutton = Menubutton(menubar, text='Edit', underline=0)
        ebutton.pack(side=LEFT)
        edit = Menu(ebutton, tearoff=False)
        edit.add_command(label='Add points', command=self.Add_points_on, underline=0)
        edit.add_command(label='Delete points', command=self.notdone, underline=0)
        edit.add_separator()
        ebutton.config(menu=edit, bg='white')

        cbutton = Menubutton(menubar, text='Calculate', underline=0)
        cbutton.pack(side=LEFT)
        calcu = Menu(cbutton, tearoff=False)
        calcu.add_command(label='Distance', command=self.notdone, underline=0)
        calcu.add_command(label='Angle', command=self.notdone,underline=0)
        calcu.add_command(label='DBH', command=self.notdone, underline=0)
        cbutton.config(menu=calcu, bg='white')

        submenu = Menu(edit, tearoff=False)
        submenu.add_command(label='Clockwise 90°', command=self.cw90,underline=0)
        submenu.add_command(label='Anti-Clockwise 90°', command=self.acw90, underline=0)
        submenu.add_command(label='Clockwise 180°', command=self.cw180, underline=0)
        edit.add_cascade(label='Rotate image', menu=submenu,underline=0)

    def notdone(self):
        showerror('Not implemented','Not yet available')

    def Add_points_on(self):
        ScrolledCanvas.NewTree_OnOff=0
        print(ScrolledCanvas.NewTree_OnOff)

    def OpenNew(self):
        ScrolledCanvas.Imagedir = r'D:\OneDrive\Program\Python\UNB\IMG_1545.JPG'
        ScrolledCanvas.Open_Picture()

    def cw90(self):
        ScrolledCanvas.Rotate += 90
        if ScrolledCanvas.Rotate == 360:
            ScrolledCanvas.Rotate = 0
        ScrolledCanvas.Open_Picture()

    def acw90(self):
        ScrolledCanvas.Rotate -= 90
        if ScrolledCanvas.Rotate == -360:
            ScrolledCanvas.Rotate = 0
        ScrolledCanvas.Open_Picture()

    def cw180(self):
        ScrolledCanvas.Rotate += 180
        if ScrolledCanvas.Rotate == 360:
            ScrolledCanvas.Rotate = 0
        ScrolledCanvas.Open_Picture()

if __name__ == '__main__':
    root = Tk()
    root.title('ImageDBH')
    MenuBar = MenuBar(root)
    MenuBar.pack(side=TOP, fill=X)
    ScrolledCanvas = ScrolledCanvas(root)
    # ScrolledCanvas.Imagedir = r'D:/OneDrive/Documents/3 UNB/本科毕业设计/Picture/IMG_1559.JPG'
    ScrolledCanvas.pack(side=TOP)
    root.mainloop()