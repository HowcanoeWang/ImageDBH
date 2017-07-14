# -*- coding:UTF-8 -*-
import traceback
import xlwt
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter.simpledialog import *
from tkinter import ttk
from PIL import ExifTags
from PIL.ImageTk import Image
from PIL.ImageTk import PhotoImage
import DBHCalculation_angle


class ScrolledCanvas(Frame):
    Imagedir = ''
    NewTree_OnOff = -1
    TreeNum = 0
    PointNum = {'UP1': [],'UP2':[], 'UC': [],'UL':[], 'DP1': [],'DP2':[], 'DC': [], 'DL':[],'Comb':[]}
    PhotoSize = []
    Rotate = 0 # []+(逆时针90度), -(顺时针90度)
    ISIN = False
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
        canvas.bind('<B1-Motion>', self.onMovePoint)
        canvas.bind('<ButtonRelease-1>', self.LooseMouse)

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

    def Open_Picture(self,event=None):
        self.ClearCanvas()
        image = Image.open(self.Imagedir)
        if self.Rotate == 90 or self.Rotate == -270:
            photo = PhotoImage(image.transpose(Image.ROTATE_270))
        elif self.Rotate == 180 or self.Rotate == -180:
            photo = PhotoImage(image.transpose(Image.ROTATE_180))
        elif self.Rotate == 270 or self.Rotate == -90:
            photo = PhotoImage(image.transpose(Image.ROTATE_90))
        else:
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
        self.PointNum = {'UP1': [],'UP2':[], 'UC': [],'UL':[],
                         'DP1': [],'DP2':[], 'DC': [], 'DL':[],
                         'DBH': [],'Comb':[]}
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
                (Cx, Cy)=self.Calcu_CentrePoints(self.PointNum['UP1'][i],
                                                 self.PointNum['UP2'][i])
                # Draw centre point
                ID_c = self.Create_Point(Cx, Cy, 'green')
                # Add centre point information to DataFrame
                self.PointNum['UC'].append(ID_c)
                # Add curve line comb
                self.PointNum['Comb'][i].append([self.PointNum['UP1'][i],
                                                 self.PointNum['UP2'][i],
                                                 self.PointNum['UC'][i]])
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
                (Cx, Cy) = self.Calcu_CentrePoints(self.PointNum['DP1'][i],
                                                   self.PointNum['DP2'][i])
                # Draw centre point
                ID_c = self.Create_Point(Cx, Cy, 'green')
                # Add centre point information to DataFrame
                self.PointNum['DC'].append(ID_c)
                # Add curve line comb
                self.PointNum['Comb'][i].append([self.PointNum['DP1'][i],
                                                 self.PointNum['DP2'][i],
                                                 self.PointNum['DC'][i]])
                # Draw curve line
                ID_l = self.Create_Curveline(self.PointNum['Comb'][i][1])
                # Add line information to DataFrame
                self.PointNum['DL'].append(ID_l)
                # Fresh OnOff index
                self.NewTree_OnOff = -1
                # Add tree Number
                self.TreeNum += 1
                global SysTemp,TreeNo
                # save points and tree number information
                SysTemp['PointPosition'][PicSelectMenu.NowPicNum] = self.Num2Position()
                SysTemp['TreeNo.'][PicSelectMenu.NowPicNum].append(TreeNo)
                PicSelectMenu.ShowInTable()

    def onMovePoint(self,event):
        # not in add point mode(make sure this click is move points rather than add points)
        if self.NewTree_OnOff == -1:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            # Select a new point, initialise self.ISIN
            if self.ISIN == False:
                idtouched = event.widget.find_closest(x, y)
                # if the canvas is empty(just open without any photo),
                #    IDtouched == (), function self.isin goes error
                if idtouched:
                    isin = self.isin(idtouched[0])
                    # if selected point belongs to PointNum,
                    #    isin returns(Ture,PointKind[int], pointLine[int],IDtouched)
                    #    e.g. ISIN = (True,1,3,2)
                    # else not in
                    #    ISIN returns (False,-1,-1,2)
                    if isin[0]:
                        self.ISIN = isin
            # Do not release mouse, keep moving
            else:
                # set selected point position == mouse position
                self.canvas.coords(self.ISIN[3], (x - 5, y - 5, x + 5, y + 5))
                Comb = self.PointNum['Comb']
                #print(Comb)
                for i in range(len(Comb)):
                    # move points are up points
                    if self.ISIN[3] in Comb[i][0]:
                        lineID = self.PointNum['UL'][i]
                        # move line
                        self.Create_Curveline(self.PointNum['Comb'][i][0],lineID)
                    # move points are down points
                    if self.ISIN[3] in Comb[i][1]:
                        lineID = self.PointNum['DL'][i]
                        # move line
                        self.Create_Curveline(self.PointNum['Comb'][i][1],lineID)

    def LooseMouse(self,event):
        global SysTemp
        if self.ISIN:
            if self.ISIN != -1:
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                # change moved point position in SysTemp file
                SysTemp['PointPosition'][PicSelectMenu.NowPicNum][self.ISIN[1]][self.ISIN[2]] = [x,y]
            PicSelectMenu.ShowInTable()
            self.ISIN = False


    def Create_Curveline(self,ID,lineID=None):
        # create_line has three points to draw curve line
        # but if these three points is P_baseL, P_baseR, and P_top
        # the curve line would scross P_centre rather than P_top
        # So we need to calculate P_top if we want the curve line across P_centre
        # (P)_baseL--------(P)_baseR
        #   \             /
        #    \   (P)_c  /
        #     \       /
        #     (P)_top
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
        # curve line returns 6 parametres while points(circle) returns 4 parameters
        if len(Position) == 4:
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
                # record the point kind in order to change SysTemp by mouse moving function
                PointKind = ['UP1','UP2', 'UC', 'DP1','DP2', 'DC'].index(i)
                PointLine = self.PointNum[i].index(ID)
        return (isin,PointLine,PointKind,ID)

    def Position2Num(self,Position):
        for j in range(len(Position)):
            P4Use = Position[j][:6]
            i = self.TreeNum
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
            self.PointNum['Comb'][i].append([self.PointNum['UP1'][i],
                                             self.PointNum['UP2'][i],
                                             self.PointNum['UC'][i]])
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
            self.PointNum['Comb'][i].append([self.PointNum['DP1'][i],
                                             self.PointNum['DP2'][i],
                                             self.PointNum['DC'][i]])
            # Draw curve line
            ID_l = self.Create_Curveline(self.PointNum['Comb'][i][1])
            # Add line information to DataFrame
            self.PointNum['DL'].append(ID_l)
            # Add tree Number
            self.TreeNum += 1

    def Num2Position(self,event=None):
        # UP1 | UP2 | UC | DP1 | DP2 | DC | PhotoSize
        PointPosition = []
        for i in range(len(self.PointNum['DC'])):
            PointPosition.append([self.ID2Position(self.PointNum['UP1'][i]),
                                  self.ID2Position(self.PointNum['UP2'][i]),
                                  self.ID2Position(self.PointNum['UC'][i]),
                                  self.ID2Position(self.PointNum['DP1'][i]),
                                  self.ID2Position(self.PointNum['DP2'][i]),
                                  self.ID2Position(self.PointNum['DC'][i]),
                                  self.PhotoSize])
        return PointPosition

    def getCamInfo(self,img,event=None):#img=Image.open(Imagedir)
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
        return info

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

        cbutton = Menubutton(menubar, text='Export', underline=0, state=DISABLED)
        cbutton.pack(side=LEFT)
        export = Menu(cbutton, tearoff=False)
        export.add_command(label='picture', command=self.notdone, underline=0)
        export.add_command(label='excel', command=self.export_excel, underline=0)
        cbutton.config(menu=export, bg='white')

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
        # set tree number as global to save it in the end of add points in ScrolledCanvas.onAddPoint
        global SysTemp,TreeNo
        TreeNo = askstring('Notice', 'Print Tree number')
        if TreeNo != None:
            if TreeNo == '':
                TreeNo = str(ScrolledCanvas.TreeNum+1)
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

    def NewProj(self):
        global Projectdir,SysTemp
        Projectdir = asksaveasfilename(title='New project', filetypes=[('DBH project', '.dbh')])
        if Projectdir != '':
            if Projectdir[-4:]=='.dbh':
                Projectdir=Projectdir[:-4]
                #print(Projectdir)
            SysTemp = {'photos': [], 'PointPosition': [], 'CamInfo':[], 'CalcuData': [],
                       'CtrlOnOff': [], 'Rotate': [], 'TreeNo.':[]}
            PicSelectMenu.AddPicbtn.config(state=NORMAL)
            self.cbutton.config(state=NORMAL)
            self.ebutton.config(state=NORMAL)
            self.fbutton.config(state=DISABLED)

    def OpenProj(self):
        global Projectdir,SysTemp
        Projectdir = askopenfilename(title='New project', filetypes=[('DBH project', '.dbh')])
        Projectdir = Projectdir[:-4]
        #print(Projectdir)
        if Projectdir != '':
            SysTemp = {'photos': [], 'PointPosition': [], 'CamInfo':[], 'CalcuData': [],
                       'CtrlOnOff': [], 'Rotate': [], 'TreeNo.':[]}
            f = open(Projectdir + '.dbh', 'r')
            SysTemp = eval(f.read())
            f.close()

            # check if the pictures are exist, if exist load, if not, let user to re-link pictures
            # **The best algorithm for this place is iteration check function and bulk replacement**
            # **(no time for me to achieve it T_T)**
            PicOk = True
            photo_folder_old = []
            photo_folder_new = []
            for photo in SysTemp['photos']:
                line = SysTemp['photos'].index(photo)
                if not os.path.exists(photo):
                    PicOk =False
                    # the next photo path is same to former successfully replaced photo path
                    if photo_folder_new and photo_folder_old == photo[:photo.rindex('/')]:
                        newphoto = photo_folder_new + '/' + photo[photo.rindex('/'):]
                        SysTemp['photos'][line] = newphoto
                        print(newphoto)
                        PicOk = True
                    # this photo is the first picture (photo_folder_old==[])
                    # or this photo's folder is different from former successfully replaced photo's folder
                    else:
                        photo_folder_old = photo[:photo.rindex('/')]
                        ans = askyesno('Image missing', photo + '\n re-link it?')
                        if ans:    # re-link
                            newphoto = askopenfilename(title='Relink:    ' + photo,
                                                       filetypes=[('Image file', photo[-4:])])
                            photo_folder_new = newphoto[:newphoto.rindex('/')]
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
                            del SysTemp['CamInfo'][line]
                            del SysTemp['TreeNo.'][line]
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

    def export_excel(self):
        global SysTemp
        Calcu_Data = SysTemp['CalcuData']
        savepath = asksaveasfilename(title='export data', filetypes=[('excelfile', '.xls')])
        print(savepath)
        if savepath != '':
            if savepath[-4:] == '.xls':
                savepath = savepath[:-4]
            wb = xlwt.Workbook(encoding='utf-8')
            i = 1
            for onepic in Calcu_Data:
                worksheet = wb.add_sheet(str(i))
                worksheet.write(0, 0, label='treenum')
                worksheet.write(0, 1, label='angle(°)')
                worksheet.write(0, 2, label='distance(m)')
                worksheet.write(0, 3, label='DBH(cm)')
                t = 1
                for onetree in onepic:
                    worksheet.write(t, 0, label=str(onetree[0]))
                    worksheet.write(t, 1, label=float(onetree[1][:-1]))
                    worksheet.write(t, 2, label=float(onetree[2][:-1]))
                    worksheet.write(t, 3, label=float(onetree[3][:-2]))
                    t += 1
                i += 1

            wb.save(savepath + '.xls')
            print('done')


    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook


class PicSelectMenu(Frame):

    def __init__(self,parent=None):
        Frame.__init__(self,parent)

        MainFrame = Frame(parent, bg='white')
        MainFrame.pack(side=BOTTOM, fill=X)

        toolbar = Frame(MainFrame, relief=SUNKEN, bd=2)
        toolbar.config(height=45, bg='white')
        toolbar.pack(side=LEFT, fill=X)
        AddPicbtn = Button(MainFrame, text='Add\nImages',
                           command=self.AddPic, bg='white', state=DISABLED)
        AddPicbtn.pack(side=RIGHT, fill=Y)


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
            SysTemp['CamInfo'][k+i] = ScrolledCanvas.getCamInfo(img=imgobj)
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
        ScrolledCanvas.Open_Picture()
        self.ShowInTable()

    def ShowInTable(self):
        global Systemp
        # show Caminfo
        CamInfo = SysTemp['CamInfo'][self.NowPicNum]
        TreeNo = SysTemp['TreeNo.'][self.NowPicNum]
        Rotate = SysTemp['Rotate'][self.NowPicNum]
        # Refresh Table Panel Information
        TableInfo.Ml.delete('0', END)
        TableInfo.Ml.insert(0, CamInfo['Model'])
        TableInfo.FL.delete('0', END)
        TableInfo.FL.insert(0, str(round(CamInfo['FocalLength'],2)))
        TableInfo.FX.delete('0', END)
        TableInfo.FX.insert(0, str(round(CamInfo['FPX'],2)))
        TableInfo.FY.delete('0', END)
        TableInfo.FY.insert(0, str(round(CamInfo['FPY'],2)))
        # get data
        # if number of trees in SysTem['CalcuData'] not equal to latest trees number
        #    which means add a new tree
        # or move a tree point
        # then refresh information in table panel
        if len(SysTemp['CalcuData'][self.NowPicNum]) != \
                len(SysTemp['PointPosition'][self.NowPicNum]) or ScrolledCanvas.ISIN:
            PointPosition = ScrolledCanvas.Num2Position()
            data = DBHCalculation_angle.output(PointPosition, CamInfo, TreeNo, Rotate)
            SysTemp['CalcuData'][self.NowPicNum] = data
        else:
            data = SysTemp['CalcuData'][self.NowPicNum]
        # show in table
        TableInfo.clearTree()
        for values in data:
            TableInfo.Tree.insert('', 'end', values=values)

    def AddPic(self):
        NewPicdirlist = list(askopenfilenames(title='Select pictures',
                                              filetypes=[('jpg files', '.jpg'),
                                                         ('png files', '.png'),
                                                         ('tif files','.tif')]))
        NewPicdir = []
        for Dir in NewPicdirlist:
            if Dir not in SysTemp['photos']:
                NewPicdir.append(Dir)
        if len(NewPicdir) != 0:
            self.AddPicButton(NewPicdir)

    def AddSysTempInfo(self):
        SysTemp['PointPosition'].append([])
        SysTemp['CamInfo'].append([])
        SysTemp['CalcuData'].append([])
        SysTemp['CtrlOnOff'].append([])
        SysTemp['Rotate'].append(0)
        SysTemp['TreeNo.'].append([])

    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!',exception_string)
    sys.excepthook = my_except_hook

class TableInfo(Frame):
    LabIndex = ['Camera Model', 'Focal Length (mm)', 'Focal X (mm)', 'Focal Y (mm)']
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        MainFrame = Frame(parent,bg='white')
        MainFrame.pack(fill=BOTH, expand=YES)

        # CamInfoFrame panel
        CamInfoFrame = Frame(MainFrame)
        CamInfoFrame.pack(side=TOP, fill=BOTH, expand=YES)
        # Model
        lab = Label(CamInfoFrame, text=self.LabIndex[0], relief=RIDGE, bg='white')
        self.Ml = Entry(CamInfoFrame, text='', relief=SUNKEN, bg='pink', justify='center')
        lab.pack(side=TOP, expand=YES, fill=BOTH)
        self.Ml.pack(side=TOP, expand=YES, fill=BOTH)
        # FocalLength
        lab = Label(CamInfoFrame, text=self.LabIndex[1], relief=RIDGE, bg='white')
        self.FL = Entry(CamInfoFrame, text='', relief=SUNKEN, bg='pink', justify='center')
        lab.pack(side=TOP, expand=YES, fill=BOTH)
        self.FL.pack(side=TOP, expand=YES, fill=BOTH)
        # FocalX
        lab = Label(CamInfoFrame, text=self.LabIndex[2], relief=RIDGE, bg='white')
        self.FX = Entry(CamInfoFrame, text='', relief=SUNKEN, bg='pink', justify='center')
        lab.pack(side=TOP, expand=YES, fill=BOTH)
        self.FX.pack(side=TOP, expand=YES, fill=BOTH)
        # FocalY
        lab = Label(CamInfoFrame, text=self.LabIndex[3], relief=RIDGE, bg='white')
        self.FY = Entry(CamInfoFrame, text='', relief=SUNKEN, bg='pink', justify='center')
        lab.pack(side=TOP, expand=YES, fill=BOTH)
        self.FY.pack(side=TOP, expand=YES, fill=BOTH)

        # Result Panel
        Tree = ttk.Treeview(MainFrame, show="headings", columns=('No.', 'Angle', 'Distance', 'DBH'))
        Tree.bind("<Double-Button-1>", self.on_tree_select)
        Tree['columns'] = ('No.', 'Angle', 'Distance', 'DBH')

        Tree.column('No.', width=50, anchor='center')
        Tree.column('Angle', width=50, anchor='center')
        Tree.column('Distance', width=60, anchor='center')
        Tree.column('DBH', width=60, anchor='center')
        Tree.heading('No.', text='No.')
        Tree.heading('Angle', text='Angle')
        Tree.heading('Distance', text='Distance')
        Tree.heading('DBH', text='DBH')
        Refresh = Label(MainFrame, text='Double click to change No.', bg='white')
        Refresh.pack(side=BOTTOM, fill=X, expand=YES)
        Tree.pack(side=BOTTOM, fill=BOTH, expand=YES)

        self.Tree = Tree

    def clearTree(self):
        TableInfo.Tree.delete(*TableInfo.Tree.get_children())

    def on_tree_select(self,event):
        TreeNo = askstring('Notice', 'Change the tree number to')
        if TreeNo != None:
            if TreeNo == '':
                showwarning(title='Warning!',message='Input should not be empty!')
            else:
                global SysTemp
                # get selected line data
                curItem = self.Tree.focus()
                curValue = list(self.Tree.item(curItem,'values'))
                # get all values in the table
                allValues = SysTemp['CalcuData'][PicSelectMenu.NowPicNum]
                # get the line number of selected data
                curNum = allValues.index(curValue)
                # refresh tree number
                SysTemp['CalcuData'][PicSelectMenu.NowPicNum][curNum][0] = TreeNo
                SysTemp['TreeNo.'][PicSelectMenu.NowPicNum][curNum] = TreeNo
                # refresh table
                PicSelectMenu.ShowInTable()

if __name__ == '__main__':
    # show trackback in errormessage

    def my_except_hook(type, value, tb):
        exception_string = "".join(traceback.format_exception(type, value, tb))
        showerror('Error!', exception_string)

    def quit_save_confirm():
        # Save project file when exit
        if Projectdir != '':  # if user do not choose any project, exist without writing project file
            ans = askyesno('warning', 'Save changes?')
            if ans:
                f = open(Projectdir + '.dbh', 'w')
                f.write(str(SysTemp))
                f.close()
        root.destroy()

    global SysTemp, Projectdir
    Projectdir=''
    SysTemp = {'photos':[],'PointPosition':[],'CamInfo':[],
               'CalcuData':[],'CtrlOnOff':[],'Rotate':[],'TreeNo.':[]}

    # main body starts
    root = Tk()
    root.title('ImageDBH')
    root.config(bg='white')
    MenuBar = MenuBar(root)
    MenuBar.pack(side=TOP, fill=X)
    PicSelectMenu = PicSelectMenu(root)
    PicSelectMenu.pack(side=BOTTOM)
    ScrolledCanvas = ScrolledCanvas(root)
    ScrolledCanvas.pack(side=LEFT)
    TableInfo = TableInfo(root)
    TableInfo.pack(side=RIGHT)
    root.protocol("WM_DELETE_WINDOW", quit_save_confirm)
    sys.excepthook = my_except_hook
    root.mainloop()