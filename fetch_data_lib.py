#!/usr/bin/python

import xml.dom.minidom
import urllib.request, urllib.parse, urllib.error
import time
import os
import sys
import cgi
import re
import datetime
import socket

baseurl = 'http://data.fmi.fi'
baseurl2 = 'http://opendata.fmi.fi'
fmiApiKey = ''
useApiKey = False

request = 'getFeature'
query = 'fmi::observations::weather::timevaluepair'
timestep = 1

def getTime(start):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - start*24*3600))

def getUrl(url):
    print("urllib.urlopen", url)
    try:
        socket.setdefaulttimeout(4)
        f = urllib.request.urlopen(url)
        print("read")
        res = f.read()
        f.close()
        return res
    except IOError:
        print("IOError:", url)
        return ""

def getText(node):
    allText = ''
    for text in node.childNodes:
        if text.nodeType == text.TEXT_NODE:
            allText = allText + text.data
    return allText.encode("utf-8")

def getMeasurements(key, station, starttime, endtime, timestep, param):
    global fmiApiKey
    fmiApiKey = key
    if useApiKey:
        query_url = baseurl + '/fmi-apikey/' + fmiApiKey
    else:
        query_url = baseurl2
    query_url = query_url + '/wfs?request=' + request + '&storedquery_id=' + query + '&fmisid=' + station +  '&parameters=' + param + '&starttime=' + starttime + '&endtime=' + endtime + '&timestep=' + str(timestep)
    #print(query_url, file=sys.stderr)
    return getUrl(query_url)

def getMeasurementsDuration(key, station, duration, param):
    if duration == 0:
        duration = (60.0*60)/24.0/3600 # 60 mins in fraction of days
    starttime = getTime(duration);
    endtime = getTime(0)
    timestep = 10
    if duration > 2:
        timestep = 30
    if duration >= 14:
        timestep = 60
    return getMeasurements(key, station, starttime, endtime, timestep, param)

def formatTime(tm):
    # 2013-03-23T09:20:00Z
    reg = re.search('([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+)Z', tm.decode('utf-8'))
    year = reg.group(1)
    month = reg.group(2)
    day = reg.group(3)
    hour = reg.group(4)
    minute = reg.group(5)
    if time.localtime().tm_isdst:
        tzone = time.altzone
    else:
        tzone = time.timezone
    d = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), 0, 0, None) - datetime.timedelta(0, tzone)
    return d.strftime('%Y,%m,%d,%H,%M,%H:%M')

def parseData(page):
    try:
        dom = xml.dom.minidom.parseString(page)
    except:
        print(page, file=sys.stderr)
        return []
    #print(page)
    members = dom.getElementsByTagName("wfs:member")
    observationsArray = []
    for member in members:
        observations = member.getElementsByTagName('omso:PointTimeSeriesObservation')
        for observation in observations:
            measurementsArray = []
            measurementsArray.append(observation.attributes["gml:id"].value)
            measurements = observation.getElementsByTagName('wml2:MeasurementTVP')
            for measurement in measurements:
                measurement_time = getText(measurement.getElementsByTagName('wml2:time')[0])
                measurementsArray.append(formatTime(measurement_time))
                measurement_value = getText(measurement.getElementsByTagName('wml2:value')[0])
                measurementsArray.append(measurement_value)
            observationsArray.append(measurementsArray)
    return observationsArray

def fetchData(key, station, starttime, endtime, timestep, parameter):
    page = getMeasurements(key, station, starttime, endtime, timestep, parameter)
    return parseData(page)

def fetchDataNumDays(key, station, number_of_days, parameter):
    page = getMeasurementsDuration(key, station, number_of_days, parameter)
    return parseData(page)

class Measurement:
    def __init__(self, time, dir, speed, gust):
        tm = time.split(',')
        self.time = datetime.datetime(int(tm[0]), int(tm[1]), int(tm[2]), int(tm[3]), int(tm[4]))
        self.dir = dir
        self.speed = speed
        self.gust = gust

def feathMeasurementsArray(station, starttime, endtime, steps, params):
    observations = fetchData(station, starttime, endtime, 30, 'winddirection,windspeedms,windgust')
    wind_dirs = observations[0]
    wind_speeds = observations[1]
    wind_gusts = observations[2]
    measurements = []
    for i in range(1, len(wind_dirs)):
        if i%2:
            measurements.append(Measurement(wind_dirs[i], float(wind_dirs[i+1]), float(wind_speeds[i+1]), float(wind_gusts[i+1])))
    return measurements
