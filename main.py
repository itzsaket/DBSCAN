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
from celluloid import Camera

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
    if path.exists("plot_geo.csv"):
        os.remove("plot_geo.csv")
    # if path.exists("plot_coordinate.csv"):
    #     os.remove("plot_coordinate.csv")


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
        # print(row)
        if row[0] == 'GPS':
            lat = row[7]
            lng = row[8]
        elif row[0] == 'ATT':
                att_yaw = float(row[-3])
        # elif row == start_point:
        #     print("check true")
        #     _check = True
        # elif row == end_point:
        #     print("check false")
        #     _check = False
        elif row[0] == 'MSG':
            if row[2] == ' Mission: 1 Takeoff':
                print("check True")
                _check = True
            elif row[2] == ' Mission: 98 RTL':
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
    df.to_csv('plot_coordinate.csv')
    dic = {'lat': list_Olat, 'lon': list_Olng}
    dfo = pd.DataFrame({key: pd.Series(value) for key, value in dic.items()})
    dfo.to_csv('plot_geo.csv')
    # plt.scatter(list_lat, list_lng)
    # plt.show()
    # sample_cluster(list_lat, list_lng)


sema = Semaphore(1)                          # semaphore for mutual exclusion
database_size = 80                           # by default database size
true_object = 0                              # object true not use currently
database_x = [0] * database_size             # coordinate x list
database_y = [0] * database_size             # coordinate y list
database_cluster_ID = [0] * database_size    # id cluster
database_verification = [0] * database_size  # data verification 0 - not verified 1 - verified
distance_glitch = 1                     # distance between points to make a point valid
x_coordinate = []                            # store valid x coordinate
y_coordinate = []                            # store valid y coordinate
ID_coordinate = []                           # coordinate cluster ID
cluster_coordinate = []                      # cluster class
Task_complete = False                        # task complete by fetching points
id_taken = 0                                 # id taken is used to alot new id to a point
dee = 0

def get_distance(x1, y1, x2, y2):
    return math.sqrt(pow((x2-x1), 2) + pow((y2-y1), 2))
def point_validit(x, y, index):
    global database_x, database_y, database_verification, database_size, x_coordinate, y_coordinate, true_object, id_taken, dee
    minimum_point = 0
    distance_glitch = 2
    for i in range(0, database_size):
        if i == index:          # same index no need to check
            continue
        if database_x[i] == 0.0 and database_y[i] == 0.0:       # zero no
            continue
        # if database_verification[i] != 0:
        #
        #     continue

        # distance = get_distance(x, y, database_x[i], database_y[i])
        coords_1 = (x, y)
        coords_2 = (database_x[i], database_y[i])

        distance = geopy.distance.geodesic(coords_1, coords_2).m
        # print(distance)
        if distance < distance_glitch:

            minimum_point += 1
            # print("setting cluster")
            # if database_cluster_ID[i] == 0:
            #     if database_cluster_ID[index] == 0:
            #         id_taken += 1
            #         print("using ID " + str(id_taken) + " "+ str(dee))
            #         database_cluster_ID[index] = id_taken
            #         database_cluster_ID[i] = database_cluster_ID[index]
            #         # backup_id = database_cluster_ID[index]
            #         # for j in range(len(database_cluster_ID)):
            #         #     if database_cluster_ID[j] == backup_id:
            #         #         database_cluster_ID[j] = backup_id
            #     elif database_cluster_ID[index] != 0:
            #         database_cluster_ID[i] = database_cluster_ID[index]
            # else:
            #     backup_id = database_cluster_ID[index]
            #     for j in range(len(database_cluster_ID)):
            #         if database_cluster_ID[j] == backup_id:
            #             database_cluster_ID[j] = backup_id

    # # now verification of
    # for k in range(0, database_size):
    #     if database_cluster_ID[k] == database_cluster_ID[index]:
    #         minimum_point += 1
            # print(minimum_point)

    if minimum_point > 20:
        database_verification[index] = 1
    # if minimum_point > 40 and database_verification[index] != 1:
    #     for l in range(0, database_size):
    #         if database_cluster_ID[l] == database_cluster_ID[index]:
    #             if database_verification[l] != 1:
    #                 database_verification[l] = 1
    #     #             x_coordinate.append(database_x[l])
    #     #             y_coordinate.append(database_y[l])
    #     #             ID_coordinate.append(database_cluster_ID[index])
    #     # x_coordinate.append(x)
    #     # y_coordinate.append(y)
    #     # print(database_cluster_ID[index])
    #     database_verification[index] = 1
    #     # ID_coordinate.append(database_cluster_ID[index])
    #     # true_object += 1


d = 0
    # print("checking cluster")
def filter_thread():

    global database_x, database_y, database_verification, database_size, Task_complete, d

    # while (True):
    #     # print("thread_working")
    #
    #     if Task_complete:
    #         print("break")
    #         break
    #     sema.acquire()
    #     # print(database_x)
    #     # print(database_y)
    #     # print(database_ID)
    for i in range(0, database_size):
        if database_x[i] == 0.0 and database_y[i] == 0.0:
            # print("ignoring")
            continue
        if database_verification[i] != 0:
            # print("point is good")
            continue
        # print("do " + str(d))
        point_validit(database_x[i], database_y[i], i)
    d += 1

        # sema.release()
        # time.sleep(0.001)
    # print("ID ")
    # print(ID_coordinate)
# lock1 = Semaphore(1)
def plotting_thread():
    global database_x, database_y, database_verification, database_size, Task_complete, true_object, dee
    # opening the CSV file
    file_read = open('plot_geo.csv',newline='')
    csv_reader = reader(file_read)
    counter = 0
    count_append = 0
    count = 0
    for i in csv_reader:
        dee = i
        count += 1
        if count >= 50:
            filter_thread()
            count = 0

        if counter == 0:
            counter += 1
            continue
        counter += 1
        sema.acquire()
        x = float(i[1])
        y = float(i[2])
        if count_append >= database_size:
            count_append = 0

        if database_verification[count_append] != 0:
            x_coordinate.append(database_x[count_append])
            y_coordinate.append(database_y[count_append])
            cluster_coordinate.append(database_cluster_ID[count_append])
        database_x[count_append] = x
        database_y[count_append] = y
        if database_verification[count_append] != 0:
            print("adding")
            database_verification[count_append] = 0
            database_cluster_ID[count_append] = 0
            true_object -= 1
        count_append += 1
        sema.release()
        time.sleep(0.001)
    print("task complete")
    Task_complete = True

# def plot_graph_thread():
#     print("plotting")
#     global x_coordinate, y_coordinate, true_object, Task_complete
#     camera = Camera(plt.figure())
#     list_x = []
#     list_y = []
#     while(True):
#         if not Task_complete:
#             continue
#         for i in range(len(x_coordinate)):
#             list_x.append(x_coordinate[i])
#             list_y.append(y_coordinate[i])
#             plt.scatter(x_coordinate, y_coordinate, s=len(x_coordinate))
#             camera.snap()
#
#         Task_complete = False
#         anim = camera.animate(blit=True)
#         anim.save('scatter.mp4')
#         # lock1.release()
#         time.sleep(0.5)


if __name__=="__main__":
    # t1 = threading.Thread(target=filter_thread, name="t1")
    # t2 = threading.Thread(target=plotting_thread, name="t2")
    # t3 = threading.Thread(target=plot_graph_thread, name="t3")
    # while(True):
    init_fs()
    read_log()

    # t1.start()
    # t2.start()
    print("plotting")
    # global x_coordinate, y_coordinate, true_object, Task_complete
    camera = Camera(plt.figure())
    list_x = []
    list_y = []
    print(len(ID_coordinate))
    print(ID_coordinate)
    bo = False
    plotting_thread()
    # while(True):
    #     if not Task_complete:
    #         continue
    #     break

    print(x_coordinate)
    dic = {'lat': x_coordinate, 'lon': y_coordinate, 'cluster number': cluster_coordinate}
    dfo = pd.DataFrame({key: pd.Series(value) for key, value in dic.items()})
    dfo.to_csv('plot_geo_good.csv')

    for i in range(len(cluster_coordinate)):
        if cluster_coordinate[i] == 0:
            continue
            i = 0
        for j in range(len(cluster_coordinate)):
            if cluster_coordinate[j] == cluster_coordinate[i]:
                list_x.append(x_coordinate[j])
                list_y.append(y_coordinate[j])
                cluster_coordinate[j] = 0
                i += 1

        if i > 0:
            print(x_coordinate)
            dic = {'lat': x_coordinate, 'lon': y_coordinate}
            dfo = pd.DataFrame({key: pd.Series(value) for key, value in dic.items()})
            dfo.to_csv('plot\plot_geo' + str(i) + '.csv')
            list_x.clear()
            list_y.clear()
 
        # break

    print("completer")

