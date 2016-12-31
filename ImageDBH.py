# -*- coding:UTF-8 -*-
import traceback
from tkinter.messagebox import *
from tkinter.filedialog import *
from PIL import ExifTags
from PIL.ImageTk import Image
from PIL.ImageTk import PhotoImage
import DBHCalculation

class ScrolledCanvas(Frame):
    ##
    Imagedir = r'D:\OneDrive\Program\Python\UNB\IMG_1545.JPG'
    NewTree_OnOff = -1
    TreeNum = 0
    PointNum = {'UP1': [],'UP2':[], 'UC': [],'UL':[], 'DP1': [],'DP2':[], 'DC': [], 'DL':[],'Comb':[]}
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
    Comb[0 [[UP1,UP2,UC] -> UL,[DP1,DP2,UC] -> DL],
         1 [[UL]              ,[DL]              ],
         2 [[]                ,[]                ],...]
    '''
    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        self.pack(expand=YES,fill=BOTH)

        canvas = Canvas(self, relief=SUNKEN)
        canvas.config(width=800, height=600, bg='white',bd=1)
        canvas.config(highlightthickness=0)
        canvas.bind('<ButtonPress-1>', self.onPutPoint)
        canvas.bind('<B1-Motion>',self.onMovePoint)
        #canvas.bind('<Double-1>', self.Num2Position)
        #canvas.bind('<Double-2>', self.Open_Picture)
        #canvas.bind('<Double-3>',self.ClearCanvas)

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
            photo = PhotoImage(image.transpose(Image.ROTATE_270))
        elif self.Rotate == 180 or self.Rotate == -180:
            photo = PhotoImage(image.transpose(Image.ROTATE_180))
        elif self.Rotate == 270 or self.Rotate == -90:
            photo = PhotoImage(image.transpose(Image.ROTATE_90))
        else:
            # photo = ImageTk.PhotoImage(image)
            photo = PhotoImage(image)
        self.photo = photo
        self.canvas.create_image(0, 0, image=photo, anchor=NW)
        self.canvas.config(scrollregion=(0,0,photo.width(),photo.height()))
        self.canvas.create_line((0,photo.height()/2,photo.width(),photo.height()/2),fill='yellow')
        self.PhotoSize=[photo.width(),photo.height()]
        # Draw points from SysTemp['PointPosition'] if it is not empty
        global SysTemp
        Position = SysTemp['PointPosition'][PicSelectMenu.NowPicNum]
        if Position != []:
            self.Position2Num(Position)

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
                #print(self.PointNum)
                global SysTemp
                SysTemp['PointPosition'][PicSelectMenu.NowPicNum] = self.Num2Position()
                #print(SysTemp['PointPosition'])

    def onMovePoint(self,event):
        if self.NewTree_OnOff == -1:# not in add point mode
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            IDtouched = event.widget.find_closest(x,y)
            ISIN = self.isin(IDtouched[0])
            if len(IDtouched)==1 and ISIN[0]:
                self.canvas.coords(IDtouched, (x-5,y-5,x+5,y+5))
                Comb = self.PointNum['Comb']
                if ISIN != -1:
                    global SysTemp
                    SysTemp['PointPosition'][PicSelectMenu.NowPicNum][ISIN[1]][ISIN[2]]=[x,y] # change moved point position in SysTemp file
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
        PointKind = -1
        PointLine = -1
        for i in ['UP1','UP2', 'UC', 'DP1','DP2', 'DC']:
            Ans = ID in self.PointNum[i]
            if Ans or False:
                isin = True
                PointKind = ['UP1','UP2', 'UC', 'DP1','DP2', 'DC'].index(i) # record the point kind in order to change SysTemp by mouse moving function
                PointLine = self.PointNum[i].index(ID)
        return (isin,PointLine,PointKind)

    def Position2Num(self,Position):
        for j in range(len(Position)):
            P4Use = Position[j][:6]
            i = self.TreeNum
            print(P4Use)
            # P4Use = [[UP1.x, UP1.y], [UP2.x, UP2.y], [UC.x, UC.y], [DP1.x, DP1.y], [DP2.x, DP2.y], [DC.x, DC.y]]
            # Draw points - UP1
            ID_p1 = self.Create_Point(P4Use[0][0], P4Use[0][1], 'blue')
            # Add information to DataFrame
            self.PointNum['UP1'].append(ID_p1)
            self.PointNum['Comb'].append([])
            # Draw points - UP2
            ID_p2 = self.Create_Point(P4Use[1][0], P4Use[1][1], 'blue')
            # Add information to DataFrame
            self.PointNum['UP2'].append(ID_p2)
            # Draw centre point - UC
            ID_c = self.Create_Point(P4Use[2][0], P4Use[2][1], 'green')
            # Add centre point information to DataFrame
            self.PointNum['UC'].append(ID_c)
            # Add curve line comb
            self.PointNum['Comb'][i].append([self.PointNum['UP1'][i], self.PointNum['UP2'][i], self.PointNum['UC'][i]])
            # Draw curve line
            ID_l = self.Create_Curveline(self.PointNum['Comb'][i][0])
            # Add line information to DataFrame
            self.PointNum['UL'].append(ID_l)
            # Draw points - DP1
            ID_p1 = self.Create_Point(P4Use[3][0], P4Use[3][1], 'red')
            # Add information to DataFrame
            self.PointNum['DP1'].append(ID_p1)
            # Draw points - DP2
            ID_p2 = self.Create_Point(P4Use[4][0], P4Use[4][1], 'red')
            # Add information to DataFrame
            self.PointNum['DP2'].append(ID_p2)
            # Draw centre point - DC
            ID_c = self.Create_Point(P4Use[5][0], P4Use[5][1], 'green')
            # Add centre point information to DataFrame
            self.PointNum['DC'].append(ID_c)
            # Add curve line comb
            self.PointNum['Comb'][i].append([self.PointNum['DP1'][i], self.PointNum['DP2'][i], self.PointNum['DC'][i]])
            # Draw curve line
            ID_l = self.Create_Curveline(self.PointNum['Comb'][i][1])
            # Add line information to DataFrame
            self.PointNum['DL'].append(ID_l)
            # Add tree Number
            self.TreeNum += 1

    def Num2Position(self,event=None):
        # UP1 | UP2 | UC | DP1 | DP2 | DC | PhotoSize + PhotoInfo
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
        # print(info)
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
        # print(PointPosition)
        return PointPosition

    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook

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
        file.add_command(label='New', command=self.NewProj, underline=0)
        file.add_command(label='Open', command=self.OpenProj, underline=1)
        file.add_command(label='Quit', command=self.Quit, underline=0)
        fbutton.config(menu=file, bg='white')

        ebutton = Menubutton(menubar, text='Edit', underline=0,state=DISABLED)
        ebutton.pack(side=LEFT)
        edit = Menu(ebutton, tearoff=False)
        edit.add_command(label='Add points', command=self.Add_points_on, underline=0)
        edit.add_command(label='Delete points', command=self.notdone, underline=0)
        edit.add_separator()
        ebutton.config(menu=edit, bg='white')

        cbutton = Menubutton(menubar, text='Calculate', underline=0,state=DISABLED)
        cbutton.pack(side=LEFT)
        calcu = Menu(cbutton, tearoff=False)
        calcu.add_command(label='Distance', command=self.Distance, underline=0)
        calcu.add_command(label='Angle', command=self.notdone,underline=0)
        calcu.add_command(label='DBH', command=self.notdone, underline=0)
        cbutton.config(menu=calcu, bg='white')

        submenu = Menu(edit, tearoff=False)
        submenu.add_command(label='Clockwise 90°', command=self.cw90,underline=0)
        submenu.add_command(label='Anti-Clockwise 90°', command=self.acw90, underline=0)
        submenu.add_command(label='Clockwise 180°', command=self.cw180, underline=0)
        edit.add_cascade(label='Rotate image', menu=submenu,underline=0)

        self.cbutton = cbutton
        self.ebutton = ebutton
        self.fbutton = fbutton

    def notdone(self):
        showerror('Not implemented','Not yet available')

    def Add_points_on(self):
        ScrolledCanvas.NewTree_OnOff=0    # activate left click to add point

    def cw90(self):
        ScrolledCanvas.Rotate += 90
        if ScrolledCanvas.Rotate == 360:
            ScrolledCanvas.Rotate = 0
        SysTemp['Rotate'][PicSelectMenu.NowPicNum] = ScrolledCanvas.Rotate
        ScrolledCanvas.Open_Picture()

    def acw90(self):
        ScrolledCanvas.Rotate -= 90
        if ScrolledCanvas.Rotate == -360:
            ScrolledCanvas.Rotate = 0
        SysTemp['Rotate'][PicSelectMenu.NowPicNum] = ScrolledCanvas.Rotate
        ScrolledCanvas.Open_Picture()

    def cw180(self):
        ScrolledCanvas.Rotate += 180
        if ScrolledCanvas.Rotate == 360:
            ScrolledCanvas.Rotate = 0
        SysTemp['Rotate'][PicSelectMenu.NowPicNum] = ScrolledCanvas.Rotate
        ScrolledCanvas.Open_Picture()

    def Distance(self):
        PointPosition = ScrolledCanvas.Num2Position()
        data=DBHCalculation.output(PointPosition)
        msg = 'Distance=' + str(data[0])+ '\n' + 'DBH=' + str(data[1])
        showinfo(title='results',message=msg)

    def NewProj(self):
        global Projectdir,SysTemp
        Projectdir = asksaveasfilename(title='New project', filetypes=[('DBH project', '.dbh')])
        if Projectdir != '':
            if Projectdir[-4:]=='.dbh':
                Projectdir=Projectdir[:-4]
                #print(Projectdir)
            SysTemp = {'photos': [], 'PointPosition': [], 'CalcuData': [], 'CtrlOnOff': [], 'Rotate': []}
            PicSelectMenu.AddPicbtn.config(state=NORMAL)
            self.cbutton.config(state=NORMAL)
            self.ebutton.config(state=NORMAL)

    def OpenProj(self):
        global Projectdir,SysTemp
        Projectdir = askopenfilename(title='New project', filetypes=[('DBH project', '.dbh')])
        Projectdir = Projectdir[:-4]
        #print(Projectdir)
        if Projectdir != '':
            SysTemp = {'photos': [], 'PointPosition': [], 'CalcuData': [], 'CtrlOnOff': [], 'Rotate': []}
            f = open(Projectdir + '.dbh', 'r')
            SysTemp = eval(f.read())
            f.close()
            # check if the pictures are exist, if exist load, if not, let user to re-link pictures
            PicOk = True
            for photo in SysTemp['photos']:
                line = SysTemp['photos'].index(photo)
                if not os.path.exists(photo):
                    PicOk =False
                    ans = askyesno('Image missing', photo + '\n re-link it?')
                    if ans:    # re-link
                        newphoto = askopenfilename(title='Relink:    ' + photo,
                                                   filetypes=[('Image file', photo[-4:])])
                        if newphoto == '':
                            showerror('Image missing', 'Could not link photos, please open other projects!')
                        else:
                            SysTemp['photos'][line] = newphoto
                            PicOk = True
                    else:    # not relink -> delete missing message
                        del SysTemp['photos'][line]
                        del SysTemp['CtrlOnOff'][line]
                        del SysTemp['PointPosition'][line]
                        del SysTemp['Rotate'][line]
                        del SysTemp['CalcuData'][line]
                        PicOk = True
            if PicOk:
                PicSelectMenu.AddPicButton(SysTemp['photos'],new=False)
                PicSelectMenu.AddPicbtn.config(state=NORMAL)
                self.cbutton.config(state=NORMAL)
                self.ebutton.config(state=NORMAL)
                self.fbutton.config(state=DISABLED)

    def Quit(self):
        ans = askokcancel('Verfy exit', "Really quit?")
        if ans:
            Frame.quit(self)
    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook

class PicSelectMenu(Frame):

    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        AddPicbtn = Button(parent,text='Add\nImages', command=self.AddPic,bg='white',state=DISABLED)
        AddPicbtn.pack(side=RIGHT, fill=Y)
        toolbar = Frame(parent, relief=SUNKEN, bd=2)
        toolbar.config(height=45, bg='white')
        toolbar.pack(side=BOTTOM, fill=X)
        self.toolbar=toolbar
        self.AddPicbtn = AddPicbtn
        self.toolPhotoDir = []
        self.AddPicButton(SysTemp['photos'])
        self.NowPicNum = 0

    def AddPicButton(self,Picdir,new=True):
        global SysTemp
        if new:
            k = len(SysTemp['photos'])
        else:
            k = 0
        for i in range(len(Picdir)):
            if new:
                SysTemp['photos'].append(Picdir[i])
                self.AddSysTempInfo()
            imgobj = Image.open(Picdir[i])
            imgobj.thumbnail((40, 40), Image.ANTIALIAS)
            img = PhotoImage(imgobj)
            btn = Button(self.toolbar, image=img, cursor='hand2')
            # print(SysTemp['photos'],k+i)
            handler = lambda savefile=(SysTemp['photos'][k + i],k+i): self.ShowInCanvas(savefile)
            btn.config(relief=RAISED, bd=2, bg='white', command=handler)
            btn.config(width=40, height=40)
            btn.pack(side=LEFT)
            self.toolPhotoDir.append((img,imgobj))    # why lack this sentence thumbnail don't show?

    def ShowInCanvas(self,savefile):
        global SysTemp
        imagedir=savefile[0];num=savefile[1]
        self.NowPicNum = num
        ScrolledCanvas.Imagedir = imagedir
        ScrolledCanvas.Rotate = SysTemp['Rotate'][self.NowPicNum]
        #print(self.NowPicNum,SysTemp['Rotate'][self.NowPicNum],ScrolledCanvas.Rotate)
        ScrolledCanvas.Open_Picture()

    def AddPic(self):
        NewPicdirlist = list(askopenfilenames(title='Select pictures',filetypes=[('jpg files', '.jpg'), ('png files', '.png'),('tif files','.tif')]))
        NewPicdir = []
        for Dir in NewPicdirlist:
            if Dir not in SysTemp['photos']:
                NewPicdir.append(Dir)
        if len(NewPicdir) != 0:
            self.AddPicButton(NewPicdir)

    def AddSysTempInfo(self):
        SysTemp['PointPosition'].append([])
        SysTemp['CalcuData'].append([])
        SysTemp['CtrlOnOff'].append([])
        SysTemp['Rotate'].append(0)

    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook

if __name__ == '__main__':
    # show trackback in errormessage
    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook
    # main body starts
    root = Tk()
    root.title('ImageDBH')
    root.config(bg='white')
    MenuBar = MenuBar(root)
    MenuBar.pack(side=TOP, fill=X)
    ScrolledCanvas = ScrolledCanvas(root)
    ScrolledCanvas.pack(side=TOP)
    global SysTemp, Projectdir
    Projectdir=''
    SysTemp = {'photos':[],'PointPosition':[],'CalcuData':[],'CtrlOnOff':[],'Rotate':[]}
    PicSelectMenu = PicSelectMenu(root)
    PicSelectMenu.pack()
    root.mainloop()
    # Save project file when exit
    if Projectdir != '':    # if user do not choose any project, exist without writing project file
        f = open(Projectdir + '.dbh', 'w')
        f.write(str(SysTemp))
        f.close()