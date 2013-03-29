#!/usr/bin/python

import xml.dom.minidom
import urllib
import time
import os
import sys
import cgi
import re
import datetime

baseurl = 'http://data.fmi.fi/'
apikey = 'b37f3e99-cdb8-4858-b850-bfffea6542f9'
request = 'getFeature'
#query = 'fmi::observations::weather::multipointcoverage'
query = 'fmi::observations::weather::timevaluepair'
#query = 'fmi::observations::weather::realtime::place::timevaluepair'
# windspeedms, temperature, winddirection
#place = 'Harmaja'
timestep = 1
#starttime = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 30*60))
#endtime = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

#query_url = baseurl + 'fmi-apikey/' + apikey + '/wfs?' + 'request=' + request + '&storedquery_id=' + query + '&place=' + place +  '&parameters=' + parameters + '&starttime=' + starttime + '&endtime=' + endtime
#'&timestep=' + str(timestep) +
#http://data.fmi.fi/fmi-apikey/b37f3e99-cdb8-4858-b850-bfffea6542f9/wfs?request=getFeature&storedquery_id=fmi::observations::weather::timevaluepair&place=jaala&timestep=30
#http://data.fmi.fi/fmi-apikey/b37f3e99-cdb8-4858-b850-bfffea6542f9/wfs?request=getFeature&storedquery_idfmi::observations::weather::timevaluepair&place=Harmaja&timestep=10


def getTime(start):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - start*24*3600))

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

def getText(node):
    allText = ''
    for text in node.childNodes:
        if text.nodeType == text.TEXT_NODE:
            allText = allText + text.data
    return allText.encode("utf-8")

def getMeasurements(station, duration, param):
    if duration == 0:
        duration = (20.0*60)/24.0/3600 # 20 mins in fraction of days
    starttime = getTime(duration);
    endtime = getTime(0)
    timestep = 10
    if duration > 2:
        timestep = 30
    if duration >= 14:
        timestep = 60
    query_url = baseurl + 'fmi-apikey/' + apikey + '/wfs?' + 'request=' + request + '&storedquery_id=' + query + '&fmisid=' + station +  '&parameters=' + param + '&starttime=' + starttime + '&endtime=' + endtime + '&timestep=' + str(timestep)
#    print query_url
    return getUrl(query_url)

def formatTime(tm):
    # 2013-03-23T09:20:00Z
    reg = re.search('([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+)Z', tm)
    year = reg.group(1)
    month = reg.group(2)
    day = reg.group(3)
    hour = reg.group(4)
    minute = reg.group(5)
    d = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), 0, 0, None) - datetime.timedelta(0, time.timezone)
    return d.strftime('%Y,%m,%d,%H,%M,%H:%M')

def fetchData(station, number_of_days, parameter):
    page = getMeasurements(station, number_of_days, parameter)
    try:
        dom = xml.dom.minidom.parseString(page)
    except:
        print >> sys.stderr, page
        sys.exit()
    #print page
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
