# -*- coding:UTF-8 -*-

def Calcu_TanTheta(RotateWH,Attribution):
    RotateX = RotateWH[0]
    RotateY = RotateWH[1]
    PicSize0 = Attribution['Size'][0]
    FocalLength = Attribution['FocalLength']   # (mm)
    if RotateX == PicSize0:   # no rotate or rotate 180
        FPX = Attribution['FPX']    # (mm)
        FPY = Attribution['FPY']    # (mm)
    else: # rotate 90°
        FPX = Attribution['FPY']    # (mm)
        FPY = Attribution['FPX']    # (mm)
    #  Theta = 1/2 FOV(Field of View)
    TanThetaX = 0.5 * FPX / FocalLength
    TanThetaY = 0.5 * FPY / FocalLength
    a = (FocalLength/FPY)*RotateY*45
    return TanThetaX,TanThetaY,a

def Judge_PointRealPosition(OneTreePoints):
    # -----------coordinate---------
    #          ● → x (bigger)
    #          ↓
    #          y (bigger)
    # ------------------------------
    # Average Y of up edge points bigger than Y of centre point => edge points lower => is real up points series
    if (OneTreePoints[0][1] + OneTreePoints[1][1]) / 2 > OneTreePoints[2][1]:
        UC = OneTreePoints[2]    # Y_up_centre
        DC = OneTreePoints[5]    # Y_down_centre
        # Judge which Up edge point is left
        if OneTreePoints[0][0] < OneTreePoints[1][0]: # Edge point1 X  < Edge point2 X
            UEL = OneTreePoints[0]    # Up edge point1 (Left)
            UER = OneTreePoints[1]    # Up edge point2 (Right)
        else:
            UEL = OneTreePoints[1]    # Up edge point1 (Left)
            UER = OneTreePoints[0]    # Up edge point2 (Right)
        # Judge which Down Point is left
        if OneTreePoints[3][0] < OneTreePoints[4][0]: # Edge point1 X  < Edge point2 X
            DEL = OneTreePoints[3]    # down edge point1 (Left)
            DER = OneTreePoints[4]    # down edge point2 (Right)
        else:
            DEL = OneTreePoints[4]    # down edge point1 (Left)
            DER = OneTreePoints[3]    # down edge point2 (Right)
    # average Y of up edge points smaller than Y of centre point => edge points higher => is opposite up points series
    else:
        UC = OneTreePoints[5]    # Y_up_centre
        DC = OneTreePoints[2]    # Y_down_centre
        # Judge which Up edge point is left
        if OneTreePoints[3][0] < OneTreePoints[4][0]: # Edge point1 X  < Edge point2 X
            UEL = OneTreePoints[3]    # Up edge point1 (Left)
            UER = OneTreePoints[4]    # Up edge point2 (Right)
        else:
            UEL = OneTreePoints[4]    # Up edge point1 (Left)
            UER = OneTreePoints[3]    # Up edge point2 (Right)
        # Judge which Down Point is left
        if OneTreePoints[0][0] < OneTreePoints[1][0]: # Edge point1 X  < Edge point2 X
            DEL = OneTreePoints[0]    # down edge point1 (Left)
            DER = OneTreePoints[1]    # down edge point2 (Right)
        else:
            DEL = OneTreePoints[1]    # down edge point1 (Left)
            DER = OneTreePoints[0]    # down edge point2 (Right)
    COC = [OneTreePoints[6][0]/2,OneTreePoints[6][1]/2]    # centre of camera
    ReadyData = {'UEL':UEL,'UER':UER,'DEL':DEL,'DER':DER,'UC':UC,'DC':DC,'COC':COC}
    return ReadyData

def Calcu_Angle(ReadyData):
    Angle = 0
    return Angle

def Calcu_DBH(ReadyData,Yscale,Dc,De):
    Xuel = ReadyData['UEL'][0]
    Xuer = ReadyData['UER'][0]
    Xdel = ReadyData['DEL'][0]
    Xder = ReadyData['DER'][0]
    Avg_x = (1/3)*(Xuer-Xuel)+(2/3)*(Xder-Xdel)
    StringX = Avg_x*Yscale['YE']
    d = 0.5*StringX
    '''
          ●
         /|  ↘
     R  / d     ↘ De
       /  |        ↘
      ○--┴------)---★
      |-   R    -|  Dc
    d*(R+Dc)=R*De => R = (Dc*d)/(De-d)
    '''
    R = (Dc * d) / (De - d)
    DBH = 2*R
    return DBH

def Calcu_Distance(ReadyData,YScale,TanY):
    YLength = YScale*ReadyData['COC'][1]*2
    D = YLength/(2*TanY)
    return D

def _Calcu_Scale(ReadyData):
    # Calculate the centre point Y scale
    # Yuc-Ymc=30cm, Ydc-Ymc=15cm, Yuc-Ydc=45cm
    Yuc = ReadyData['UC'][1]
    Ydc = ReadyData['DC'][1]
    Ymc = ReadyData['COC'][1]     # centre of camera
    #YScale_C1 = 30/abs(Yuc-Ymc)    # (cm/pix)
    #YScale_C2 = 15/abs(Ydc-Ymc)    # (cm/pix)
    YScale_C3 = 45/abs(Yuc-Ydc)    # (cm/pix)
    #YScale_C = (YScale_C1 + YScale_C2 + YScale_C3)/3 # (cm/pix)
    YScale_C =YScale_C3
    # Calculate the edge point Y scale
    Yuel = ReadyData['UEL'][1]
    Yuer = ReadyData['UER'][1]
    Ydel = ReadyData['DEL'][1]
    Yder = ReadyData['DER'][1]
    #YScale_EL1 = 30/abs(Yuel-Ymc)    # (cm/pix)
    #YScale_ER1 = 30/abs(Yuer-Ymc)    # (cm/pix)
    #YScale_EL2 = 15/abs(Ydel-Ymc)    # (cm/pix)
    #YScale_ER2 = 15/abs(Yder-Ymc)    # (cm/pix)
    YScale_EL3 = 45/abs(Yuel-Ydel)   # (cm/pix)
    YScale_ER3 = 45/abs(Yuer-Yder)   # (cm/pix)
    #YScale_EL = (YScale_EL1 + YScale_EL2 + YScale_EL3)/3    # (cm/pix)
    #YScale_ER = (YScale_ER1 + YScale_ER2 + YScale_ER3)/3    # (cm/pix)
    YScale_E = (YScale_EL3 + YScale_ER3)/2
    YScale = {'YE':YScale_E,'YC':YScale_C}
    return YScale

def output(PointPosition, CamInfo, TreeNo):
    # Calcudata=[[No., Angle, Distance, DBH].
    #            [No., Angle, Distance, DBH]...]
    CalcuData = []
    for i in range(len(PointPosition)):
        #print(PointPosition[i],i)
        #TanX,TanY,a = Calcu_TanTheta(PointPosition[i][6],PointPosition[i][7])
        TanX, TanY, a = Calcu_TanTheta(PointPosition[i][6], CamInfo)
        Ready_Data = Judge_PointRealPosition(PointPosition[i])
        #print(Ready_Data)
        YScale = _Calcu_Scale(Ready_Data)
        Ag = Calcu_Angle(Ready_Data)
        Dc = Calcu_Distance(Ready_Data,YScale['YC'],TanY)
        De = Calcu_Distance(Ready_Data,YScale['YE'],TanY)
        #print(Dc,De)
        DBH = Calcu_DBH(Ready_Data, YScale, Dc, De)
        #print(DBH)
        CalcuData.append([TreeNo[i], str(Ag)+'°', str(round(Dc/100,2))+'m', str(round(DBH,2))+'cm'])
    return CalcuData

if __name__ == '__main__':
    # test data
    PointPosition = [
        [[940.0, 1295.0], [1070.0, 1296.0], [1005.0, 1291.0], [952.0, 1486.0], [1117.0, 1483.0], [1035.0, 1488.0],
         [1944, 2592]]]
    CamInfo={'FocalLength': 5.8, 'FPY': 4.2672, 'Model': 'Canon PowerShot SD430 WIRELESS', 'FPX': 5.715,
                        'Size': (2592, 1944)}
    output(PointPosition,CamInfo)