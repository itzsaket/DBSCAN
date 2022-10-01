import os

import numpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import geopy
import geopy.distance
import pandas as pd
import os
from os import path
from csv import reader
from csv import reader


# q_lat = 28.41597778
# q_lng = 77.00401111
# q_lat = 28.41620000
# q_lng = 77.00384167
q_lat = 28.41641111
q_lng = 77.00456944

start_point = ["MSG"," 1049560672"," Mission: 1 Takeoff"]
end_point = ["MSG"," 1085781277"," Mission: 6 WP"]

# wrap an angle into 360 degrees
def wrap360(ang):
    if(ang < 360):
        return ang
    ang = ang%360

    return ang


def get_quardent(lat, lng):
    if q_lat <= lat and q_lng <= lng:
        lat = lat - q_lat
        lng = lng - q_lng
    elif q_lat > lat and q_lng <= lng:
        lat = q_lat - lat
        lng = lng - q_lng
    elif q_lat > lat and q_lng > lng:
        lat = q_lat - lat
        lng = q_lng - lng
    elif q_lat <= lat and q_lng > lng:
        lat = lat - q_lat
        lng = q_lng - lng
    return lat, lng

def init_fs():
    if path.exists("plot_raw.csv"):
        os.remove("plot_raw.csv")
    if path.exists("plot_geo.csv"):
        os.remove("plot_geo.csv")

def read_log():

    #file read currently manully set the file name to read by the code
    file_read = open("data.log",newline='')
    csv_reader = reader(file_read)
    lat = 0.0
    lng = 0.0
    list_lat = []
    list_lng = []
    list_Olat = []
    list_Olng = []
    att_yaw = 0.0
    _check = False
    for row in csv_reader:

        if row[0] == 'GPS':
            lat = row[7]
            lng = row[8]
        elif row[0] == 'ATT':
                att_yaw = float(row[-3])
        elif row == start_point:
            print("check true")
            _check = True
        elif row == end_point:
            print("check false")
            _check = False
        elif row[0] == 'R21F' and _check:

            dis = row[-3]
            ang = float(row[-2])
            ang = wrap360(att_yaw + ang)
            if float(dis) > 0.0:
                lat2, lon2, r = geopy.distance.distance(kilometers=float(dis) / 1000).destination(
                    (float(lat), float(lng)), bearing=ang)
                list_Olat.append(lat2)
                list_Olng.append(lon2)
                r_lat, r_lng = get_quardent(lat2, lon2)
                # print(list_lon)
                list_lat.append(r_lat)
                list_lng.append(r_lng)
        elif row[0] == 'R21B' and _check:
            dis = row[-3]
            ang = float(row[-2])
            ang = wrap360(att_yaw + ang)
            if float(dis) > 0.0:
                lat2, lon2, r = geopy.distance.distance(kilometers=float(dis) / 1000).destination(
                    (float(lat), float(lng)), bearing=ang)
                list_Olat.append(lat2)
                list_Olng.append(lon2)
                r_lat, r_lng = get_quardent(lat2, lon2)
                # print(list_lon)
                list_lat.append(r_lat)
                list_lng.append(r_lng)
    dict = {'lat': list_lat, 'lon': list_lng}
    df = pd.DataFrame({key: pd.Series(value) for key, value in dict.items()})
    dic = {'lat': list_Olat, 'lon': list_Olng}
    df = pd.DataFrame({key: pd.Series(value) for key, value in dic.items()})
    df.to_csv('plot_geo.csv')
    plt.scatter(list_lat, list_lng)
    plt.show()

if __name__=="__main__":
    init_fs()
    read_log()