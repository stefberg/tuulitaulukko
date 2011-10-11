#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.dom.minidom
import urllib
import time
import os
import sys

url = 'http://www.emhi.ee/ilma_andmed/xml/observations.php'
infoUrl = 'http://www.emhi.ee/index.php?ide=15&v_kiht=1'
codes = ["86093", "86094", "26122", "26115", "26218", "26231"]
stationsTable = {}

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

page = getUrl(url)
if page.find('<?xml') != 0:
    sys.exit()

try:
    dom = xml.dom.minidom.parseString(page)
except:
    print >> sys.stderr, page
    sys.exit()

observations = dom.getElementsByTagName("observations")
timestamp = observations[0].attributes["timestamp"].value
time=time.localtime(float(timestamp))
day=time[2]
hour=time[3]
minute=time[4]

stations = observations[0].getElementsByTagName("station")

for station in stations:
    wmocode = station.getElementsByTagName("wmocode")[0].childNodes[0].data
    if wmocode in stationsTable:
        stationsTable[wmocode].append(station)
    else:
        stationsTable[wmocode] = [ station ]

def getText(node):
    allText = ''
    for text in node.childNodes:
        if text.nodeType == text.TEXT_NODE:
            allText = allText + text.data
    return allText.encode("utf-8")

if "SERVER_NAME" in os.environ:
    print 'Content-Type: text/html'
    print ''
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
print '  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">'
print '  <head>'
print '    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>'
print '    <title>Eesti Asemat</title>'
print '    <style type="text/css">'
print '    v\:* {'
print '      behavior:url(#default#VML);'
print '    }'
print 'body { margin:0;padding:0; color:#3D3D33; font:10px verdana,arial,sans-serif; line-height:1.4; text-align:left; } table {font:10px verdana, arial, sans-serif;border:0;text-align:left;}'
print 'table.lboardsnip { background-color:#fff;text-align:center;width:140px;font-size:9px;border-collapse:collapse;}'
print 'table.lboardsnip td, table.lboardsnip th { border:1px solid #999;padding:3px 1px; vertical-align:middle;}'
print 'table.lboardsnip tr.head th {background-color:#3D3D33;color:#CCCCC2;font-weight:normal;}'
print 'table.lboardsnip tr.odd {background-color:#CCCCC2;}'
print 'table.lboardsnip tr.even {background-color:#DCDCD2;}'
print 'table.lboardsnip tr.oldtime {color:#909090; background-color:#DCDCD2;}'
print 'table.lboardsnip tr.foot td {background-color:#AAAAA0;font-weight:normal;padding-left:4px;}'
print 'table.lboardsnip .lal {padding-left:4px;}'
print '.larr {background:url(http://i.pga.com/pga/images/pgachampionship/img/icon_linkarrR.gif) no-repeat;padding-left:6px;display:inline;font-size:10px;font-weight:bold; }'
print '.lal {text-align:left;}'
print 'a:link, a:visited, a:hover, a:active {font-weight:bold;text-decoration:none;color:#3D3D33;}'
print 'a:hover {text-decoration:underline;}'
print 'td {white-space:nowrap}'
print '    </style>'
print '<META HTTP-EQUIV="REFRESH" CONTENT="600">'
print '  </head>'

print '    <table class="lboardsnip" cellpadding="0" cellspacing="0">'
print '      <tbody>'
print '	<tr class="head">'
print '	  <th colspan="6"'
print '	      style="padding-left: 4px;" align="left">'
print '	    <div style="margin-top: 4px;">Eesti asemat ' + str(hour) + ':' + str(minute) + '</div>'
print '	  </th>'
print '	</tr>'

print '	<tr class="even">'
print '	  <td class="lal"><b>Asema</b></td>'
print '	  <td ><b>Suunta</b></td>'
print '	  <td ><b>Keski</b></td>'
print '	  <td ><b>Max</b></td>'
print '	  <td ><b>T</b></td>'
print '	</tr>'

odd = 1
for code in codes:
    for station in stationsTable[code]:
        print '	<tr class="',
        if odd:
            print "odd",
        else:
            print "even",
        print '">'
        odd = 1 - odd
        print '	  <td align="left"><a href="' + infoUrl + '"><b>' + getText(station.getElementsByTagName("name")[0]) + '</b></a></td>'
        print '	  <td>' + getText(station.getElementsByTagName("winddirection")[0]) + '</td>'
        print '	  <td>' + getText(station.getElementsByTagName("windspeed")[0]) + '</td>'
        print '	  <td>' + getText(station.getElementsByTagName("windspeedmax")[0]) + '</td>'
        print '	  <td>' + getText(station.getElementsByTagName("airtemperature")[0]) + '&deg;</td>'
        print '	</tr>'

print '      </tbody>'
print '    </table>'
print '<a href="http://www.emhi.ee/index.php?ide=14&nlan=eng">Eesti Ennusteet</a>'
print ' </html>'

#<airtemperature>1.7</airtemperature>
#<winddirection>177</winddirection>
#<windspeed>16.9</windspeed>
#<windspeedmax>22.9</windspeedmax>
