#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xml.dom.minidom
import urllib.request, urllib.error, urllib.parse
import time
import os
import sys

url = 'http://www.ilmateenistus.ee/ilma_andmed/xml/observations.php'
infoUrl = 'http://www.emhi.ee/index.php?ide=15&v_kiht=1'
codes = ["86093", "86094", "26120", "26115", "26218", "26231"]

def getUrl(url):
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    return urllib.request.urlopen(req).read()

def gatherAllStationData():
    page = getUrl(url)

    htmlCode = []

    if page.find('<?xml') != 0:
        return htmlCode

    try:
        dom = xml.dom.minidom.parseString(page)
    except:
        print(page, file=sys.stderr)
        return htmlCode

    observations = dom.getElementsByTagName("observations")
    timestamp = observations[0].attributes["timestamp"].value
    tm=time.localtime(float(timestamp))
    day=tm[2]
    hour=tm[3]
    minute=tm[4]

    stations = observations[0].getElementsByTagName("station")

    stationsTable = {}

    for station in stations:
        if len(station.getElementsByTagName("wmocode")) > 0 and len(station.getElementsByTagName("wmocode")[0].childNodes):
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
        htmlCode.append('Content-Type: text/html\n')
        htmlCode.append('\n')
    htmlCode.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n')
    htmlCode.append('  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
    htmlCode.append('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">\n')
    htmlCode.append('  <head>\n')
    htmlCode.append('    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>\n')
    htmlCode.append('    <title>Eesti Asemat</title>\n')
    htmlCode.append('    <style type="text/css">\n')
    htmlCode.append('    v\:* {\n')
    htmlCode.append('      behavior:url(#default#VML);\n')
    htmlCode.append('    }\n')
    htmlCode.append('body { margin:0;padding:0; color:#3D3D33; font:10px verdana,arial,sans-serif; line-height:1.4; text-align:left; } table {font:10px verdana, arial, sans-serif;border:0;text-align:left;}\n')
    htmlCode.append('table.lboardsnip { background-color:#fff;text-align:center;width:140px;font-size:9px;border-collapse:collapse;}\n')
    htmlCode.append('table.lboardsnip td, table.lboardsnip th { border:1px solid #999;padding:3px 1px; vertical-align:middle;}\n')
    htmlCode.append('table.lboardsnip tr.head th {background-color:#3D3D33;color:#CCCCC2;font-weight:normal;}\n')
    htmlCode.append('table.lboardsnip tr.odd {background-color:#CCCCC2;}\n')
    htmlCode.append('table.lboardsnip tr.even {background-color:#DCDCD2;}\n')
    htmlCode.append('table.lboardsnip tr.oldtime {color:#909090; background-color:#DCDCD2;}\n')
    htmlCode.append('table.lboardsnip tr.foot td {background-color:#AAAAA0;font-weight:normal;padding-left:4px;}\n')
    htmlCode.append('table.lboardsnip .lal {padding-left:4px;}\n')
    htmlCode.append('.larr {background:url(http://i.pga.com/pga/images/pgachampionship/img/icon_linkarrR.gif) no-repeat;padding-left:6px;display:inline;font-size:10px;font-weight:bold; }\n')
    htmlCode.append('.lal {text-align:left;}\n')
    htmlCode.append('a:link, a:visited, a:hover, a:active {font-weight:bold;text-decoration:none;color:#3D3D33;}\n')
    htmlCode.append('a:hover {text-decoration:underline;}\n')
    htmlCode.append('td {white-space:nowrap}\n')
    htmlCode.append('    </style>\n')
    htmlCode.append('<META HTTP-EQUIV="REFRESH" CONTENT="600">\n')
    htmlCode.append('  </head>\n')

    htmlCode.append('    <table class="lboardsnip" cellpadding="0" cellspacing="0">\n')
    htmlCode.append('      <tbody>\n')
    htmlCode.append('	<tr class="head">\n')
    htmlCode.append('	  <th colspan="6"\n')
    htmlCode.append('	      style="padding-left: 4px;" align="left">\n')
    htmlCode.append('	    <div style="margin-top: 4px;">Eesti asemat ' + str(hour) + ':' + str(minute) + '</div>\n')
    htmlCode.append('	  </th>\n')
    htmlCode.append('	</tr>\n')

    htmlCode.append('	<tr class="even">\n')
    htmlCode.append('	  <td class="lal"><b>Asema</b></td>\n')
    htmlCode.append('	  <td ><b>Suunta</b></td>\n')
    htmlCode.append('	  <td ><b>Keski</b></td>\n')
    htmlCode.append('	  <td ><b>Max</b></td>\n')
    htmlCode.append('	  <td ><b>T</b></td>\n')
    htmlCode.append('	</tr>\n')

    odd = 1
    for code in codes:
        for station in stationsTable[code]:
            htmlCode.append('	<tr class="')
            if odd:
                htmlCode.append("odd")
            else:
                htmlCode.append("even")
            htmlCode.append('">\n')
            odd = 1 - odd
            htmlCode.append('	  <td align="left"><a href="' + infoUrl + '"><b>' + getText(station.getElementsByTagName("name")[0]) + '</b></a></td>\n')
            htmlCode.append('	  <td>' + getText(station.getElementsByTagName("winddirection")[0]) + '</td>\n')
            htmlCode.append('	  <td>' + getText(station.getElementsByTagName("windspeed")[0]) + '</td>\n')
            htmlCode.append('	  <td>' + getText(station.getElementsByTagName("windspeedmax")[0]) + '</td>\n')
            htmlCode.append('	  <td>' + getText(station.getElementsByTagName("airtemperature")[0]) + '&deg;</td>\n')
            htmlCode.append('	</tr>\n')

    htmlCode.append('      </tbody>\n')
    htmlCode.append('    </table>\n')
    htmlCode.append('<a href="http://www.emhi.ee/index.php?ide=14&nlan=eng">Eesti Ennusteet</a>\n')
    htmlCode.append(' </html>\n')
    return htmlCode
