PointPosition = [[[883.0, 1013.0], [1186.0, 1027.0], [1051.0, 1011.0], [851.0, 1419.0], [1168.0, 1424.0], [1016.0, 1427.0], [1944, 2592],
                  {'FPY': 4.2672, 'Size': (2592, 1944), 'FPX': 5.715, 'FocalLength': 5.8, 'Model': 'Canon PowerShot SD430 WIRELESS'}]]
def Calcu_Angle(OneTreePoints):
    Angle = 0
    return Angle

def Calcu_DBH():
    pass

def Calcu_Distance():
    pass

def Calcu_Scale(OneTreePoints):
    # Yuc-Ymc=30cm, Ydc-Ymc=15cm, Yuc-Ydc=45cm
    Yuc = OneTreePoints[2][1] # Y_up_centre
    Ydc = OneTreePoints[5][1] # Y_down_centre
    Ymc = OneTreePoints[6][1]/2 # centre of camera
    Scale_F1 = 30/abs(Yuc-Ymc)
    Scale_F2 = 15/abs(Ydc-Ymc)
    Scale_F3 = 45/abs(Yuc-Ydc)
    print(Scale_F1,Scale_F2,Scale_F3)
    Scale = (Scale_F1 + Scale_F2 + Scale_F3)/3
    return Scale
for i in range(len(PointPosition)):
    Calcu_Scale(PointPosition[i])