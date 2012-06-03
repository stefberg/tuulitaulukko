#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import urllib
import string
from HTMLParser import HTMLParser
import re
import os
import sys

tm = time.time()
time=time.localtime(tm)
hour=time.tm_hour
minute=time.tm_min

entityChars = {"auml" : "ä", "ouml" : "ö", "aring" : "å", "nbsp" : " ", "Auml" : "Ä", "Ouml" : "Ö", "Aring" : "å"}

stations = [ ("remlog", "leikosaari", "http://www.remlog.com/cgi/tplog.pl?node=leikosaari"),
             ("remlog", "villinginluoto", "http://www.remlog.com/cgi/tplog.pl?node=villinginluoto"),
             ("remlog", "apinalahti", "http://www.remlog.com/cgi/tplog.pl?node=apinalahti"),
#             ("remlog", "kalliosaari", "http://www.remlog.com/cgi/tplog.pl?node=kalliosaari"),
#             ("ilml", "Rankki", "station=2976&place=Kotka"), 
#             ("ilml", "Emäsalo", "station=2991&place=Porvoo"), 
#             ("ilml", "Kalbådagrund", "station=2987&place=Porvoo"),
             ("ilml", "Eestiluoto", "station=2930&place=Helsinki"),
#             ("ilml", "Kaisaniemi", "station=2978&place=Helsinki"),
             ("ilml", "Harmaja", "station=2795&place=Helsinki"),
#             ("ilml", "Hel.Majakka", "station=2989&place=Helsinki"),
             ("saapalvelu", "koivusaari", "/helsinki/index.php"),
             ("bw", "eira", "http://eira.poista.net/lastWeather", "http://eira.poista.net/logWeather"),
             ("bw", "nuottaniemi", "http://eps.poista.net/lastWeather", "http://eps.poista.net/logWeather"),
#             ("ilml", "Bågaskär", "station=2984&place=Inkoo"),
             ("ilml", "Jussarö", "station=2757&place=Raasepori"),
             ("remlog", "silversand", "http://www.remlog.com/tuuli/hanko.html"),
             ("ilml", "Tulliniemi", "station=2746&place=Hanko"),
#             ("ilml", "Russarö", "station=2982&place=Hanko"),
#             ("ilml", "Isokari", "station=2964&place=Kustavi"),
#             ("ilml", "Rauma", "station=2761&place=Rauma"),
#             ("yyteri", "yyteri", "http://surfkeskus.dyndns.org/saa/"),
             ("ilml", "Tahkoluoto", "station=2751&place=Pori")
#             ("ilml", "Tankar", "station=2721&place=Kokkola"),
#             ("ilml", "Ulkokalla", "station=2907&place=Kalajoki")
             ]

XXstations = [ ("saapalvelu", "Koivusaari", "/helsinki/index.php")
             ]
ilmlurl = "http://ilmatieteenlaitos.fi/suomen-havainnot?p_p_id=stationstatusportlet_WAR_fmiwwwweatherportlets&p_r_p_1689542720_parameter=21&"
fmiurl = "http://legacy.fmi.fi/saa/paikalli.html?param=21&"
remlog = "http://www.remlog.com/cgi/tplast.pl?node="
yyteriUrl="http://surfkeskus.dyndns.org/saa/"
saapalveluUrl="http://www.saapalvelu.fi"

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

oldLimitMin = 100

def oldTime(tm):
    hm = tm.split(':')
    if len(hm) < 2:
        return False
    hr = int(hm[0])
    min = int(hm[1])
#    print hour, minute, hr, min, oldLimitMin
    if hour >= hr:
        return hour * 60 + minute - (hr * 60 + min) > oldLimitMin
    return 24*60 - hour * 60 + minute + (hr * 60 + min) > oldLimitMin    


ind=0

class ILMLParser(HTMLParser):
    
    def __init__(self, info_url):
        HTMLParser.__init__(self)
        self.inObservations = False
        self.inParameterNameValue = False
        self.inParameterName = False
        self.inParameterValue = False
        self.inTimeStamp = False
        self.observationType = ''
        self.parameterValues = {"time":"na", "wind_dir":"na", "wind_speed":"na", "Puuska":"na","Lämpötila":"na"}
        self.found = False
        self.time = 'na'
        self.wind_dir = 'na'
        self.wind_speed = 'na'
        self.wind_max = 'na'
        self.info_url = info_url

    def handle_starttag(self, tag, attrs):
        if tag == "span" and self.inParameterNameValue:
            for a in attrs:
                if a[0] == "class" and a[1] == "parameter-value":
                    self.inParameterValue = True
                    self.text = ""
        if tag == "span" and self.inParameterNameValue:
            for a in attrs:
                if a[0] == "class" and a[1] == "parameter-name":
                    self.inParameterName = True
                    self.text = ""
        if tag == "span" and self.inObservations:
            for a in attrs:
                if a[0] == "class":
                    if a[1] == "parameter-name-value":
                        self.inParameterNameValue = True
                        self.text = ""
                    else:
                        if a[1] == "time-stamp":
                            self.inTimeStamp = True
                            self.text = ""

        if tag == "table":
            for a in attrs:
                if a[0] == "class" and a[1] == "observation-text":
                    self.inObservations = True

    def handle_endtag(self, tag):
        if tag == "span":
            if self.inParameterName:
                reg = re.search('([^ ]*)tuulta', self.text)
                if reg:
                    self.parameterValues["wind_dir"] = reg.group(1)
                    self.observationType = "wind_speed"
                else:
                    reg = re.search('(Tyyntä)', self.text)
                    if reg:
                        self.parameterValues["wind_dir"] = reg.group(1)
                        self.parameterValues["wind_speed"] = "0"
                        self.observationType = ''
                    else:
                        self.observationType = self.text
            self.inParameterName = False
            if self.inParameterValue:
                if self.observationType == "wind_speed" or self.observationType == "Puuska":
                    reg = re.search('([0-9]*)m/s', self.text)
                    if reg:
                        self.parameterValues[self.observationType] = reg.group(1)
                else:
                    if self.observationType == "Lämpötila":
                        reg = re.search('([-,0-9]*)', self.text)
                        if reg:
                            self.parameterValues[self.observationType] = reg.group(1)
                    else:
                        self.parameterValues[self.observationType] = self.text
                self.inParameterValue = False
                self.observationType = ''
            if self.inTimeStamp:
                reg = re.search('([0-9]+:[0-9]+)', self.text)
                if reg:
                    self.found = True
                    self.parameterValues["time"] = reg.group(1)
                    self.inTimeStamp = False

    def handle_entityref(self, char):
        if (self.inParameterName or self.inTimeStamp) and char in entityChars:
            self.text = self.text + entityChars[char]

    def handle_data(self, data):
        global ind
        if self.inParameterName or self.inParameterValue or self.inTimeStamp:
            self.text = self.text + data

class FMIParser(HTMLParser):
    
    def __init__(self, info_url):
        HTMLParser.__init__(self)
        self.havainto = False
        self.found = False
        self.time = 'na'
        self.wind_dir = 'na'
        self.wind_speed = 'na'
        self.wind_max = 'na'
        self.info_url = info_url

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for a in attrs:
                if a[0] == "class" and a[1] == "observation-text":
                    self.havainto = True
                    self.text = ""
        if tag == "br" and self.havainto:
            self.text = self.text + ' '

    def handle_endtag(self, tag):
        if tag == "p" and self.havainto:
            self.found = True
            self.havainto = False
            fields = self.text.split(';')
            reg = 0
            if len(fields) > 0:
                reg = re.search('([0-9]+:[0-9]+)', fields[0])
            if reg:
                self.time  = reg.group(1)
            for f in [ 0, 1, 2, 3, 4, 5 ]:
                reg = 0
                if len(fields) > f:
                    reg = re.search(' ([^ ]*)tuulta ([0-9]*) m/s', fields[f])
                if reg:
                    self.wind_dir = reg.group(1)
                    self.wind_speed = reg.group(2)
                reg = 0
                if len(fields) > f:
                    reg = re.search('(tyyntä)', fields[f])
                if reg:
                    self.wind_dir = reg.group(1)
                    self.wind_speed = 0
                reg = 0
                if len(fields) > f:
                    reg = re.search('puuska ([0-9]*) m/s', fields[f])
                if reg:
                    self.wind_max = reg.group(1)

    def handle_entityref(self, char):
        if self.havainto and char in entityChars:
            self.text = self.text + entityChars[char]

    def handle_data(self, data):
        global ind
        if self.havainto:
            self.text = self.text + data

class RemlogParser(HTMLParser):
    
    def __init__(self, info_url):
        HTMLParser.__init__(self)
        self.havainto = False
        self.time = 0
        self.wind_dir = 0
        self.wind_speed = 0
        self.wind_low = 0
        self.wind_max = 0
        self.temp = 0
        self.info_url = info_url
        self.found = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.havainto = True
            self.text = ""

    def handle_endtag(self, tag):
        if tag == "body" and self.havainto:
            self.havainto = False
#            print self.text
            reg = re.search('([0-9]+:[0-9]+)[ \t]*Dir: *([0-9]+)[ \t]*Low: *([0-9]+\.[0-9]+)[ \t]*Avg: *([0-9]+\.[0-9]+).*High: *([0-9]+\.[0-9]+).*Temp: *([0-9]+\.[0-9]+)', self.text)
            if reg:
                self.time  = reg.group(1)
                self.wind_dir = reg.group(2)
                self.time  = reg.group(1)
                self.wind_dir = reg.group(2)
                self.wind_low = reg.group(3)
                self.wind_speed = reg.group(4)
                self.wind_max = reg.group(5)
                self.temp = reg.group(6)
                self.found = True

    def handle_data(self, data):
        if self.havainto:
            self.text = self.text + " " + data

class YyteriParser(HTMLParser):
    
    def __init__(self, info_url):
        HTMLParser.__init__(self)
        self.table = []
        self.time = 0
        self.wind_dir = 0
        self.wind_speed = 0
        self.wind_low = 0
        self.wind_max = 0
        self.temp = 'na'
        self.info_url = info_url
        self.found = False
        self.intable = False;
        self.row = -1
        self.column = -1
        self.text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.intable = True
            self.text = ""
        if tag == "tr" and self.intable:
            self.row += 1
            self.column = -1
            self.table.append([])
        if tag == "td" and self.intable:
            self.column += 1
            self.text = ""
            self.table[self.row].append("")
            
    def handle_endtag(self, tag):
        if tag == "td" and self.column > -1 and self.row > -1:
            self.table[self.row][self.column] = self.text
        if tag == "table" and self.row > -1 and len(self.table[self.row]) > 6:
            tm = self.table[self.row][0].split(" ")
            if len(tm) > 2:
                self.time = tm[2]
            self.wind_dir = self.table[self.row][2]
            self.wind_low = self.table[self.row][4]
            self.wind_speed = self.table[self.row][5]
            self.wind_max = self.table[self.row][6]
            self.temp = self.table[self.row][7]
            self.found = True

    def handle_data(self, data):
        self.text = self.text + " " + data

def onlyAscii(a):
    b=''
    for i in range(0, len(a)):
        if string.printable.find(a[i]) >= 0:
            b = b+a[i]
    return b

class SaapalveluParser(HTMLParser):
    
    def __init__(self, info_url):
        HTMLParser.__init__(self)
        self.table = []
        self.time = 0
        self.wind_dir = 0
        self.wind_speed = 0
        self.wind_low = 0
        self.wind_max = 0
        self.temp = 'na'
        self.info_url = info_url
        self.found = False
        self.intable = False;
        self.intd = False;
        self.intemp = False
        self.inwind = False
        self.inspan = False
        self.row = -1
        self.column = -1
        self.text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.intable = True
            self.text = ""
        if tag == "tr" and self.intable:
            self.row += 1
            self.column = -1
        if tag == "td" and self.intable:
            self.intd = True
            self.text = ""
        if tag == "span":
            self.inspan = True
            self.text = ""
            
    def handle_endtag(self, tag):
        if tag == "table":
            self.intable = False
            self.intemp = False
            self.inwind = False
            self.text = ""
        if tag == "td":
            self.intd = False
            self.text = ""
        if tag == "span":
            self.inspan = False
            self.text = ""

    def handle_data(self, data):
        self.text = self.text + " " + data
        if self.intable and self.intd:
            if self.text.startswith(" Lmptila"):
                self.intemp = True
            if self.text.startswith(" Tuuli"):
                self.intuuli = True
            if self.text.startswith(" Tuulen nopeus") and self.intuuli:
                self.found = True
                reg = re.search('([0-9]+\.[0-9]+) m/s', self.text)
                if reg:
                    self.wind_speed = reg.group(1)
            if self.text.startswith(" Puuskatuuli") and self.intuuli:
                reg = re.search('([0-9]+\.[0-9]+) m/s', self.text)
                if reg:
                    self.wind_max = reg.group(1)
            if self.text.startswith(" Tuulen suunta") and self.intuuli:
                reg = re.search(' ([0-9]+)', self.text)
                if reg:
                    self.wind_dir = reg.group(1)
            if self.text.startswith(" T ll  hetkell") and self.intemp:
                reg = re.search(' ([0-9]+\.[0-9])', self.text)
                if reg:
                    self.temp = reg.group(1)
        if self.text.startswith(" P ivittynyt viimeksi:") and self.inspan:
            reg = re.search(' ([0-9]+:[0-9]+)', self.text)
            if reg:
                self.time = reg.group(1)
                

#page = getUrl(yyteriUrl)
#parser = YyteriParser("")
#parser.feed(page)
#print parser.time
#print parser.wind_dir
#print parser.wind_speed
#print parser.wind_max
#exit()

#23:45  Dir: 225 ^ 225  Low:  1.0 -  1.8  Avg:  2.1  High:  2.4 -  3.0   10.8?C
class bwParser:

    def __init__(self, info_url):
        self.time = 0
        self.wind_dir = 0
        self.wind_low = 0
        self.wind_speed = 0
        self.wind_max = 0
        self.temp = 0
        self.found = False
        self.info_url = info_url

    def parse(self, url):
        self.text = getUrl(url)
        if len(self.text) < 10:
            return
        reg = re.search('([0-9]+:[0-9]+)[ \t]*Dir:[ \t]*([0-9]+)[ \t]*.*Low:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*Avg:[ \t]*([0-9\.]+)[ \t]*High:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*([-0-9\.]+)', self.text)
        if reg:
            self.time  = reg.group(1)
            self.wind_dir = reg.group(2)
            self.wind_low = reg.group(4)
            self.wind_speed = reg.group(5)
            self.wind_max = reg.group(7)
            self.temp = reg.group(8)
            self.found = True

#parser = bwParser()
#parser.parse("e/lastWeather")
#print parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max
#parser.parse("m/lastWeather")
#print parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max
#exit()

list = []

for v in stations:
    try:
        type = v[0]
        if type == "remlog":
            page = getUrl(remlog + v[1])
            parser = RemlogParser(v[2])
            parser.feed(page)
            parser.close()
            if parser.found:
                list.append([v[1], parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max, parser.temp, parser.info_url])
        elif type == "fmi":
            page = getUrl(fmiurl + v[2])
            parser = FMIParser(fmiurl + v[2])
            parser.feed(page)
            parser.close()
            if parser.found:
                list.append([v[1], parser.time, parser.wind_dir, 0, parser.wind_speed, parser.wind_max, "", parser.info_url])
        elif type == "ilml":
            page = getUrl(ilmlurl + v[2])
            parser = ILMLParser(ilmlurl + v[2])
            parser.feed(page)
            parser.close()
            if parser.found:
                list.append([v[1], parser.parameterValues["time"], parser.parameterValues["wind_dir"], 0, parser.parameterValues["wind_speed"], parser.parameterValues["Puuska"], parser.parameterValues["Lämpötila"], parser.info_url])
        elif type == "bw":
            parser = bwParser(v[3])
            parser.parse(v[2])
            if parser.found:
                list.append([v[1], parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max, parser.temp, parser.info_url])
        elif type == "yyteri":
            page = getUrl(yyteriUrl)
            parser = YyteriParser(v[2])
            parser.feed(page)
            if parser.found:
                list.append([v[1], parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max, parser.temp, parser.info_url])
        elif type == "saapalvelu":
            page = getUrl(saapalveluUrl+v[2])
            parser = SaapalveluParser(saapalveluUrl+v[2])
            page = page.replace('sc\'+\'ript', 'script', 2)
            parser.feed(onlyAscii(page))
            if parser.found:
                list.append([v[1], parser.time, parser.wind_dir, parser.wind_low, parser.wind_speed, parser.wind_max, parser.temp, parser.info_url])

    except IOError:
        print "IOError on ", v[1]

if "SERVER_NAME" in os.environ:
    print 'Content-Type: text/html'
    print ''
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
print '  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">'
print '  <head>'
print '    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>'
print '    <title>Tuulet</title>'
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
print 'a:link, a:visited, a:hover, a:active {text-decoration:none;color:#3D3D33;}'
print 'a:hover {text-decoration:underline;}'
print 'td {white-space:nowrap}'
print '    </style>'
print '<META HTTP-EQUIV="REFRESH" CONTENT="600">'
print '    <script type="text/javascript" src="wind_data/sylvester.js">'
print '    </script>'
print '    <script type="text/javascript" src="wind_data/history_graph.js">'
print '    </script>'
print '    <script>'
print '      window.onload = function(){'
print '      setDataDir("wind_data/");'
print '      initGraph(false);'
print '      };'
print '    </script>'
print '  </head>'

print '<table  cellpadding="0" cellspacing="0">'
print '  <tr>'
print '    <td>'
print '    <table class="lboardsnip" cellpadding="0" cellspacing="0">'
print '      <tbody>'
print '	<tr class="head">'
print '	  <th colspan="6"'
print '	      style="padding-left: 4px;" align="left">'
print '	    <div style="margin-top: 4px;">Tuulet</div>'
print '	  </th>'
print '	</tr>'

print '	<tr class="even">'
print '	  <td class="lal"><b>Asema</b></td>'
print '	  <td ><b>Aika</b></td>'
print '	  <td ><b>Suunta</b></td>'
print '	  <td ><b>Keski</b></td>'
print '	  <td ><b>Max</b></td>'
print '	  <td ><b>T</b></td>'
print '	</tr>'

odd = 1

for l in list:
    print '	<tr class="',
    if oldTime(str(l[1])):
        print "oldtime",
    else:
        if odd:
            print "odd",
        else:
            print "even",
    print '">'
    odd = 1 - odd
    print '	  <td align="left"><a href="' + str(l[7]) + '"><b>' + str(l[0]) + '</b></a></td>'
    print '	  <td>' + str(l[1]) + '</td>'
    print '	  <td><a href="javascript:showStation(\'' + str(l[0]) + '\', 2)">' + str(l[2]) + '</a></td>'
    print '	  <td><a href="javascript:showStation(\'' + str(l[0]) + '\', 0)">' + str(l[4]) + '</a></td>'
    print '	  <td><a href="javascript:showStation(\'' + str(l[0]) + '\', 0)">' + str(l[5]) + '</a></td>'
    print '	  <td><a href="javascript:showStation(\'' + str(l[0]) + '\', 1)">' + str(l[6]) + '&deg;</a></td>'
    print '	</tr>'

print '      </tbody>'
print '    </table>'
print '    </td>'
print '    <td>'
print '   <div id="station_name"></div>'
print '  <canvas id="graphCanvas" width="600" height="300">'
print '    </canvas>'
print '   <select title="Select number of days to show" name="days" id="days"'
print '   style="display:none" onchange="changeDays(this.value);">'
print '      <option selected value="2">2 päivää</option>'
print '      <option value="4">4 päivää</option>'
print '      <option value="7">viikko</option>'
print '      <option value="14">2 viikkoa</option>'
print '      <option value="28">4 viikkoa</option>'
print '    </select>'
print '    <div id="debug"></div>'
print '    </td>'
print '  </tr>'
print '    </table>'

print '<a href="forecasts.html">Ennusteet</a><br/>'
print '<a href="winds_ee.html">Eesti asemat</a>'
print '<br/><br/>'
print ' </html>'
#dir = 'ttt/'
if os.uname()[1] == 'kopsu.com':
    dir = '/home/webadmin/kopsu.com/html/wind_data/'
else:
    dir = '/hsphere/local/home/saberg/dlarah.org/wind_data/'
stationsFile = 'stations.txt'

sf = open(dir + stationsFile, "w")
sf.write(str(time.tm_year) + "," + str(time.tm_yday))
sf.write("\n")
for l in list:
    sf.write(l[0])
    sf.write("\n")
    datafile = dir + l[0] + "_" + str(time.tm_year) + "-" + str(time.tm_yday) + ".txt"
    lastline = []
    if os.path.exists(datafile):
        f = open(datafile, "r+")
        for line in f:
            if len(line.split(',')) > 6:
                lastline = line.split(',')
    else:
        f = open(datafile, "w")
    if len(lastline) == 0 or lastline[5] != l[1]:
        f.write(str(time.tm_year) + ',' + str(time.tm_mon) + ',' + str(time.tm_mday) + ',' + str(time.tm_hour) + ',' + str(time.tm_min) + ',' + str(l[1]) + ',' + str(l[2]) + ',' + str(l[3]) + ',' + str(l[4]) + ',' + str(l[5]) + ',' + str(l[6].replace(',','.')))
        f.write("\n")
    f.close()
sf.close()
