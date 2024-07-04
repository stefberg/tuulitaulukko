#!/usr/bin/python3
# -*- coding: utf-8 -*-

import winds_lib
import os
import time

apikey = ''

def getApiKey():
    global apikey
    if not apikey:
        if os.uname()[1] == 'kopsu.com':
            dir = '/home/webadmin/kopsu.com/winds/'
        elif os.uname()[1] == 'Macintosh.local' or os.uname()[1] == 'Taru-MacBook-Pro-4.local':
            dir = './'
        elif os.uname()[2].find("amzn") > 0:
            dir = "/var/www/keys/"
        else:
            dir = os.environ.get("HOME") + "/"
        api_key_file = dir + 'fmi_api_key.txt'
        #print(os.uname()[1])
        #print("APIKEY file", api_key_file)
        f = open(api_key_file, "r")
        apikey = f.read();
        apikey = apikey.replace('\n', '')
        f.close()
    return apikey

#os.environ["TZ"] = "Europe/Helsinki"
#time.tzset()

(htmlCode, list) = winds_lib.gatherAllStationData(getApiKey())
for l in htmlCode:
    print(l, end=' ')

def updateStationsFile(list):
    if os.uname()[1] == 'kopsu.com':
        dir = '/home/webadmin/kopsu.com/html/wind_data/'
    elif os.uname()[1] == 'Macintosh.local' or os.uname()[1] == 'Taru-MacBook-Pro-4.local':
        dir = './wind_data/'
    elif os.uname()[2].find("amzn") > 0:
        dir = "/var/www/html/wind_data/"
    else:
        dir = os.environ.get("HOME") + '/wind_data/'

    stationsFile = 'stations.txt'

    tm = time.time()
    timeObj=time.localtime(tm)

    sf = open(dir + stationsFile, "w")
    sf.write(str(timeObj.tm_year) + "," + str(timeObj.tm_yday))
    sf.write("\n")
    for l in list:
        sf.write(l.name)
        sf.write("\n")
        datafile = dir + l.name + "_" + str(timeObj.tm_year) + "-" + str(timeObj.tm_yday) + ".txt"
        lastline = []
        if os.path.exists(datafile):
            f = open(datafile, "r+")
            for line in f:
                if len(line.split(',')) > 6:
                    lastline = line.split(',')
        else:
            f = open(datafile, "w")
        if len(lastline) == 0 or lastline[5] != l.time:
            f.write(str(timeObj.tm_year) + ',' + str(timeObj.tm_mon) + ',' + str(timeObj.tm_mday) + ',' + str(timeObj.tm_hour) + ',' + str(timeObj.tm_min) + ',' + str(l.time) + ',' + str(l.wind_dir) + ',' + str(l.wind_low) + ',' + str(l.wind_speed) + ',' + str(l.wind_max) + ',' + str(l.temp).replace(',','.'))
            f.write("\n")
            f.close()
    sf.close()

updateStationsFile(list)
