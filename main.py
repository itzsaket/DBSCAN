import csv
import math
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

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import style

import psutil
import collections
import seaborn as sns
import threading
import time
from threading import *

epsilon = 0 # the radius of a neighborhood centered on a given point

sns.set()

# q_lat = 28.41597778
# q_lng = 77.00401111
# q_lat = 28.41620000
# q_lng = 77.00384167
q_lat = 28.41641111
q_lng = 77.00456944

start_point = ["MSG"," 1057402335"," Mission: 3 WP"]
# end_point = ["MSG"," 1085781277"," Mission: 6 WP"]
# start_point = ["MSG"," 1270853105"," Mission: 27 WP"]
# end_point = ["MSG"," 1275123088"," Mission: 30 WP"]
end_point = ["MSG"," 1275123088"," Mission: 30 WP"]

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

            dis = row[-5]
            ang = float(row[-4])
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
            dis = row[-5]
            ang = float(row[-4])
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
    if path.exists("plot_coordinate.csv"):
        os.remove("plot_coordinate.csv")
    df.to_csv('plot_coordinate.csv')
    dic = {'lat': list_Olat, 'lon': list_Olng}
    dfo = pd.DataFrame({key: pd.Series(value) for key, value in dic.items()})
    if path.exists("plot_geo.csv"):
        os.remove("plot_geo.csv")
    dfo.to_csv('plot_geo.csv')
    # plt.scatter(list_lat, list_lng)
    # plt.show()
    # sample_cluster(list_lat, list_lng)

x = 0.0
y = 0.0

sema = Semaphore(1)

database_size = 80
database_x = [0] * database_size
database_y = [0] * database_size
database_ID = [0] * database_size    # id verification
distance_glitch = 0.002
def get_distance(x1, y1, x2, y2):
    return math.sqrt(pow((x2-x1), 2) + pow((y2-y1), 2))
def point_validit(x, y, index):
    global database_x, database_y, database_ID, database_size, distance_glitch
    minimum_point = 0
    for i in range(0, database_size):
        if i == index:
            continue
        if database_x[i] == 0.0 and database_y[i] == 0.0:
            continue
        if database_ID[i] != 0:
            continue
        distance = get_distance(x, y, database_x[i], database_y[i])
        if (distance < distance_glitch):
            minimum_point += 1
    if minimum_point > 10:
        database_ID[index] = 1
    else:
        database_ID[index] = 0

    # print("checking cluster")
def filter_thread():
    global database_x, database_y, database_ID, database_size
    while(True):
        # print("thread_working")
        sema.acquire()
        print(database_x)
        print(database_y)
        print(database_ID)
        for i in range(0, database_size):
            if database_x[i] == 0.0 and database_y[i] == 0.0:
                continue
            if database_ID[i] != 0:
                print("point is good")
                continue
            point_validit(database_x[i], database_y[i], i)

        sema.release()
        time.sleep(0.5)


def plotting_thread():
    global database_x, database_y, database_ID, database_size
    # opening the CSV file
    file_read = open('plot_coordinate.csv',newline='')
    csv_reader = reader(file_read)
    counter = 0
    count_append = 0
    global x, y
    for i in csv_reader:
        if counter == 0:
            counter += 1
            continue
        counter += 1
        sema.acquire()
        x = float(i[1])
        y = float(i[2])
        if count_append >= database_size:
            count_append = 0

        database_x[count_append] = x
        database_y[count_append] = y
        database_ID[count_append] = 0
        count_append += 1

        sema.release()
        time.sleep(0.5)

if __name__=="__main__":
    t1 = threading.Thread(target=filter_thread, name="t1")
    t2 = threading.Thread(target=plotting_thread, name="t2")
    # while(True):
    init_fs()
    read_log()

    t1.start()
    t2.start()

