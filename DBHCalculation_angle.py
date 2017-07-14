# -*- coding:UTF-8 -*-
from mpl_toolkits.mplot3d import Axes3D
from math import sqrt, sin, cos, atan, degrees
import matplotlib.pyplot as plt


def judge_points_rank(OneTreePoints):
    # -----------coordinate---------
    #          ● → x (bigger)
    #          ↓
    #          y (bigger)
    # ------------------------------
    # Average Y of up edge points bigger than Y of centre point => edge points lower => is real up points series
    if (OneTreePoints[0][1] + OneTreePoints[1][1]) / 2 > OneTreePoints[2][1]:
        uc = OneTreePoints[2]    # Y_up_centre
        dc = OneTreePoints[5]    # Y_down_centre
        # Judge which Up edge point is left
        if OneTreePoints[0][0] < OneTreePoints[1][0]:   # Edge point1 X  < Edge point2 X
            ul = OneTreePoints[0]    # Up edge point1 (Left)
            ur = OneTreePoints[1]    # Up edge point2 (Right)
        else:
            ul = OneTreePoints[1]    # Up edge point1 (Left)
            ur = OneTreePoints[0]    # Up edge point2 (Right)
        # Judge which Down Point is left
        if OneTreePoints[3][0] < OneTreePoints[4][0]:   # Edge point1 X  < Edge point2 X
            dl = OneTreePoints[3]    # down edge point1 (Left)
            dr = OneTreePoints[4]    # down edge point2 (Right)
        else:
            dl = OneTreePoints[4]    # down edge point1 (Left)
            dr = OneTreePoints[3]    # down edge point2 (Right)
    # average Y of up edge points smaller than Y of centre point => edge points higher => is opposite up points series
    else:
        uc = OneTreePoints[5]    # Y_up_centre
        dc = OneTreePoints[2]    # Y_down_centre
        # Judge which Up edge point is left
        if OneTreePoints[3][0] < OneTreePoints[4][0]:   # Edge point1 X  < Edge point2 X
            ul = OneTreePoints[3]    # Up edge point1 (Left)
            ur = OneTreePoints[4]    # Up edge point2 (Right)
        else:
            ul = OneTreePoints[4]    # Up edge point1 (Left)
            ur = OneTreePoints[3]    # Up edge point2 (Right)
        # Judge which Down Point is left
        if OneTreePoints[0][0] < OneTreePoints[1][0]:   # Edge point1 X  < Edge point2 X
            dl = OneTreePoints[0]    # down edge point1 (Left)
            dr = OneTreePoints[1]    # down edge point2 (Right)
        else:
            dl = OneTreePoints[1]    # down edge point1 (Left)
            dr = OneTreePoints[0]    # down edge point2 (Right)
    coc = [OneTreePoints[6][0]/2, OneTreePoints[6][1]/2]    # centre of camera
    ready_data = {'UL': ul, 'UR': ur, 'DL': dl, 'DR': dr, 'UC': uc, 'DC': dc, 'COC': coc}
    return ready_data


def pixels2xoy(readyData, PointPosition_6, caminfo, rotate=0):
    '''
    #        ●B
    #    ●A      ●C
    # ----------------------
    # ----------------------
    #  ●D          ●E
    #        ●F
            
    rotate = 0, [90, -270], 180, [270, -90]
    if rotate = 0 or 180:
        width, height = width, height
    else 
        width, height = height, width
        
     <----width---->  
            ↑y
     ┌──────┼──────┐        ^
     │      ┆      │        |
    ┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄>x   height
     │      ┆      │        |
     └──────┼──────┘        v
    '''   
    xoy = {'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': []}
    
    # According to rotate angle, exchange width & height, FPX & FPY
    fpmax = max(caminfo['FPX'], caminfo['FPY'])
    fpmin = min(caminfo['FPX'], caminfo['FPY'])
    f = caminfo['FocalLength']
    
    if rotate == 0 or rotate == 180:  # no need to exchange
        width = PointPosition_6[0]
        height = PointPosition_6[1]
    else:   # need to exchange height and width
        width = PointPosition_6[1]
        height = PointPosition_6[0]
 
    if width > height:
        fpw = fpmax
        fph = fpmin
    else:
        fpw = fpmin
        fph = fpmax
    print(width, height, fpw, fph, f)
    
    # transfer pixelWH to coordinate
    def normalize(pixel_w_h):
        # X=x/width, Y=y/height, X,Y∈ [0,1]
        (x, y) = pixel_w_h
        # void next step denomination=0 error
        if x == 0.5 * width:
            x += 0.1
        if y == 0.5 * height:
            y += 0.1
        (X, Y) = [x/width, y/height]
        x_new = (X - 0.5) * fpw
        y_new = (0.5 - Y) * fph
        return [x_new, y_new, f]   # unit is mm
    
    xoy['A'] = normalize(readyData['UL'])
    xoy['B'] = normalize(readyData['UC'])
    xoy['C'] = normalize(readyData['UR'])
    xoy['D'] = normalize(readyData['DL'])
    xoy['E'] = normalize(readyData['DC'])
    xoy['F'] = normalize(readyData['DR'])

    return xoy


def real_coordinate_calculation(xoy, distance):
    theta = 0   # default horizontal 0 degree
    f = xoy['A'][2]
    xyz = {'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': []}

    def theta_and_xyz_calculation(UP, DP):
        '''
        :param UP: xoy['A']
        :param DP: xoy['D']
        :return: tanθ
        '''
        (x1, y1, _) = UP
        (x2, y2, _) = DP

        tan_theta = (f * (1/x1 - 1/x2)) / (y1/x1 - y2/x2)
        radians_theta = atan(tan_theta)
        theta = degrees(radians_theta)

        Ux = Dx = distance*10 / (y1/x1 - y2/x2)
        Uy, Dy = y1/x1 * Ux, y2/x2 * Dx
        Uz, Dz = Uy*f / y1, Dy*f / y2

        # transverse coordinate with theta to real vertical coordinate
        # x no change, y & z change (yoz view)
        Uz_r = Uz*cos(radians_theta) - Uy*sin(radians_theta)
        Uy_r = Uz*sin(radians_theta) + Uy*cos(radians_theta)
        Dz_r = Dz*cos(radians_theta) - Dy*sin(radians_theta)
        Dy_r = Dz*sin(radians_theta) + Dy*cos(radians_theta)

        return  theta, [Ux, Uy_r, Uz_r], [Dx, Dy_r, Dz_r]

    (theta_l, xyz['A'], xyz['D']) = theta_and_xyz_calculation(xoy['A'], xoy['D'])
    (theta_c, xyz['B'], xyz['E']) = theta_and_xyz_calculation(xoy['B'], xoy['E'])
    (theta_r, xyz['C'], xyz['F']) = theta_and_xyz_calculation(xoy['C'], xoy['F'])

    theta_true = (abs(theta_l - theta_c) + abs(theta_r - theta_c)) / 2

    print(theta_l, theta_c, theta_r, theta_true)
    print(xyz)

    #three_d_view(xyz)
    return xyz, theta_true


def Circle_calculation(A,B,C):
    ### Method 1
    # xoz coordinate
    (Ax, _, Ay) = A
    (Bx, _, By) = B
    (Cx, _, Cy) = C
    # AB mid
    mid1x = (Ax + Bx) / 2
    mid1y = (Ay + By) / 2
    # BC mid
    mid2x = (Ax + Cx) / 2
    mid2y = (Ay + Cy) / 2
    # 求出分别与直线AB，BC垂直的直线的斜率
    # Calculate the slope of the vertical line with the AB and BC
    if By - Ay != 0:
        k1 = -(Bx - Ax) / (By - Ay)
        # y - mid1y = k1(x - mid1x)
    else:
        k1 = 'NaN'
        # x = mid1x

    if Cy - Ay != 0:
        k2 = -(Cx - Ax) / (Cy - Ay)
        # y - mid2y = k2(x - mid2x)
    else:
        k2 = 'NaN'
        # x = mid2x

    if k1 == 'NaN':
        Center_x = mid1x
        Center_y = mid2y + k2 * (mid1x - mid2x)
    elif k2 == 'NaN':
        Center_x = mid2x
        Center_y = mid1y + k1 * (mid2x - mid1x)
    else:
        Center_x = (mid2y - mid1y - k2 * mid2x + k1 * mid1x) / (k1 - k2)
        Center_y = mid1y + k1 * (mid2y - mid1y - k2 * mid2x + k2 * mid1x) / (k1 - k2)

    ### Method2
    A1 = Ax - Bx
    B1 = Ay - By
    C1 = (Ax**2 -Bx**2 + Ay**2 - By **2) /2
    A2 = Cx - Bx
    B2 = Cy - By
    C2 = (Cx**2 -Bx**2 + Cy**2 -By**2)/2
    temp = A1*B2 - A2*B1
    if temp == 0:
        Center_X = Ax
        Center_Y = Ay
    else:
        Center_X = (C1*B2 - C2*B1)/temp
        Center_Y = (A1*C2 - A2*C1)/temp

    # Distance calculation
    def distance_calculation(x1, y1, x2, y2):
        d = sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return d

    D2O = distance_calculation(Center_X, Center_Y, 0, 0)
    R1 = distance_calculation(Center_X, Center_Y, Ax, Ay)
    R2 = distance_calculation(Center_X, Center_Y, Bx, By)
    R3 = distance_calculation(Center_X, Center_Y, Cx, Cy)
    print(D2O, R1)
    return D2O-R1, R1


def three_d_view(xyz_real):
    # data prepare
    data_x = [0,
              xyz_real['A'][0], xyz_real['B'][0], xyz_real['C'][0],
              xyz_real['D'][0], xyz_real['E'][0], xyz_real['F'][0]]
    data_y = [0,
              xyz_real['A'][1], xyz_real['B'][1], xyz_real['C'][1],
              xyz_real['D'][1], xyz_real['E'][1], xyz_real['F'][1]]
    data_z = [0,
              xyz_real['A'][2], xyz_real['B'][2], xyz_real['C'][2],
              xyz_real['D'][2], xyz_real['E'][2], xyz_real['F'][2]]
    # plot3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    labels = ['O', 'A', 'B', 'C', 'D', 'E', 'F']
    ax.plot(data_x[1:], data_y[1:], data_z[1:], 'o',label=labels)
    plt.show()


def output(PointPosition, CamInfo, TreeNo, Rotate, distance=45):
    # calcu_data=[[No., Angle, Distance, DBH].
    #            [No., Angle, Distance, DBH]...]
    calcu_data = []
    for i in range(len(PointPosition)):
        Ready_Data = judge_points_rank(PointPosition[i])
        XOY= pixels2xoy(Ready_Data, PointPosition[i][6], CamInfo, Rotate)
        XYZ, Theta = real_coordinate_calculation(XOY, distance)
        Dc1, R1 = Circle_calculation(XYZ['A'], XYZ['B'], XYZ['C'])
        Dc2, R2 = Circle_calculation(XYZ['D'], XYZ['E'], XYZ['F'])
        Dc = (Dc1+Dc2)/20
        DBH = (R1 + R2)/10
        print(Dc, DBH)
        calcu_data.append([str(TreeNo[i]), str(round(Theta,1))+'°', str(round(Dc/100,2))+'m', str(round(DBH,2))+'cm'])
    return calcu_data

if __name__ == '__main__':
    # test data 1
    #PointPosition = [[[336.0, 2545.0], [394.0, 2547.0], [365.0, 2543.0], [357.0, 2729.0], [413.0, 2728.0], [384.0, 2731.0],[3744, 5616]]]
    CamInfo={'Size': (26, 40), 'Model': 'Canon EOS 5D Mark II', 'FocalLength': 20.0, 'FPX': 37.0586, 'FPY': 24.3332}
    Rotate = 0
    #Original_result = ['2', '0°', '7.25m', '13.69cm']
    # test data 2
    PointPosition = [[[1564.0, 2532.0], [2093.0, 2527.0], [1821.0, 2450.0], [1482.0, 2863.0], [2188.0, 2872.0], [1820.0, 2940.0], [3744, 5616]]]

    CalcuData = output(PointPosition, CamInfo, [1], Rotate)
    print(CalcuData)