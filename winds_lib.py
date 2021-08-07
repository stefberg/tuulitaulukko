#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import datetime
from datetime import timedelta
import urllib.request, urllib.parse, urllib.error
import string
import traceback
from html.parser import HTMLParser
import re
import os
import sys
import fetch_data_lib
import math

ms_to_knts = (3.6 / 1.852)

entityChars = {"auml" : "ä", "ouml" : "ö", "aring" : "å", "nbsp" : " ", "Auml" : "Ä", "Ouml" : "Ö", "Aring" : "å"}
fmiApiKey = ''

stations = [ 
    ("FmiBeta", "Emäsalo", "101023"),
    ("FmiBeta", "Kalbådagrund", "101022"),
    #             ("Remlog", "leikosaari", "http://www.remlog.com/cgi/tplog.pl?node=leikosaari"),
    #             ("Remlog", "villinginluoto", "http://www.remlog.com/cgi/tplog.pl?node=villinginluoto"),
    #             ("Remlog", "apinalahti", "http://www.remlog.com/cgi/tplog.pl?node=apinalahti", '', 'self.wind_speed>=5 and self.wind_dir>=75 and self.wind_dir<=290'),
#    ("FmiBeta", "Eestiluoto", "101029", '', 'self.wind_speed>=7 and self.wind_dir>=75 and self.wind_dir<=290'),
    ("FmiBeta", "Itätoukki", "105392", '', 'self.wind_speed>=7'),
    ("Windguru", "Villinginluoto", "id_station=1137&password=vitsiPorkkana12", '', 'self.wind_speed>=6 and self.wind_dir>=75 and self.wind_dir<=290'),
    ("FmiBeta", "Hel.Majakka", "101003"),
    ("FmiBeta", "Harmaja", "100996", '', 'self.wind_speed>=7 and self.wind_dir>=180 and self.wind_dir<=240'),
    ("Windguru", "Laru", "id_station=47&password=contribyte", '', 'self.wind_speed>=6 and self.wind_dir>=180 and self.wind_dir<=240'),
    #?({"return":"error","message":"Unauthorized API access!"});

#             ("Saapalvelu", "koivusaari", "/helsinki/index.php", '', 'self.wind_speed>=6 and self.wind_dir>=180 and self.wind_dir<=240'),
             ("Bw", "eira", "http://eira.poista.net/lastWeather", "http://eira.poista.net/logWeather", 'self.wind_max>=6 and self.wind_dir>=180+10 and self.wind_dir<=240+10'), # 10 deg off at the moment
    #             ("Bw", "nuottaniemi", "http://eps.poista.net/lastWeather", "http://eps.poista.net/logWeather"),
             ("FmiBeta", "Bågaskär", "100969"),
    ("FmiBeta", "Jussarö", "100965"),
    ("Omasaa", "Mulan", "/mulan/", '', 'self.wind_speed>=7 and ( self.wind_dir>=78 or self.wind_dir<=20 )'),
    #             ("Remlog", "silversand", "http://www.remlog.com/tuuli/hanko.html"),
             ("FmiBeta", "Tulliniemi", "100946", '', 'self.wind_speed>=8 and self.wind_dir>=78 and self.wind_dir<=205'),
    ("FmiBeta", "Russarö", "100932"),
    #("Holfuy", "Bergön", "k=s114", '', ''),
             ("FmiBeta", "Vänö", "100945"),
    ("FmiBeta", "Utö", "100908"),
    #             ("Yyteri", "yyteri", "http://www.purjelautaliitto.fi/yyteriweather/", '', 'self.wind_speed>=5 and self.wind_dir>=170 and self.wind_dir<=315'),
             ("FmiBeta", "Tahkoluoto", "101267", '', 'self.wind_speed>=8 and self.wind_dir>=170 and self.wind_dir<=315'),
    ("FmiBeta", "Tankar", "101661"),
    ("FmiBeta", "Ulkokalla", "101673"),
    ("FmiBeta", "Marjaniemi", "101784"),
    ("FmiBeta", "Vihreäsaari", "101794"),
]

spots = [ 
    ('Laru', 
     (  # one star condition
         ('Harmaja', 'self.wind_speed>=7 and self.wind_dir>=180 and self.wind_dir<=240'),
         ('Laru', 'self.wind_speed>=6 and self.wind_dir>=180 and self.wind_dir<=240'),
         ('eira', 'self.wind_max>=6 and self.wind_dir>=180+10 and self.wind_dir<=240+10') # seems 10 deg off
     ),
     (  # two star condition
         ('Harmaja', 'self.wind_speed>=8 and self.wind_dir>=185 and self.wind_dir<=235'),
         ('Laru', 'self.wind_speed>=7 and self.wind_dir>=185 and self.wind_dir<=235'),
         ('eira', 'self.wind_max>=7 and self.wind_dir>=185+10 and self.wind_dir<=235+10')
     ),
     (  # three star condition
         ('Harmaja', 'self.wind_speed>=10 and self.wind_dir>=186 and self.wind_dir<=220'),
         ('Laru', 'self.wind_speed>=8 and self.wind_dir>=186 and self.wind_dir<=220'),
         ('eira', 'self.wind_max>=8 and self.wind_dir>=186+10 and self.wind_dir<=220+10')
     )
 ),
    ('Kallvik', 
     ( # one star condition
         ('Eestiluoto', 'self.wind_speed>=7 and self.wind_dir>=75 and self.wind_dir<=290'),
         ('apinalahti', 'self.wind_speed>=5 and self.wind_dir>=75 and self.wind_dir<=290')
     ),
     ( # two star condition
         ('Eestiluoto', 'self.wind_speed>=9 and self.wind_dir>=100 and self.wind_dir<=180'),
         ('apinalahti', 'self.wind_speed>=7 and self.wind_dir>=100 and self.wind_dir<=180')
     )
 ),
    ('Eira', 
     ( # one star condition
         ('Harmaja', 'self.wind_speed>=7 and self.wind_dir>=110 and self.wind_dir<=200'),
         ('eira', 'self.wind_max>=6 and self.wind_dir>=110+10 and self.wind_dir<=200+10')
     ),
     ( # two star condition
         ('Harmaja', 'self.wind_speed>=9 and self.wind_dir>=120 and self.wind_dir<=180'),
         ('eira', 'self.wind_max>=7 and self.wind_dir>=120+10 and self.wind_dir<=180+10')
     )
 ),
    ('Tullari', 
     ( # one star condition
         ('Tulliniemi', 'self.wind_speed>=8 and self.wind_dir>=78 and self.wind_dir<=205'),
     ),
     ( # two star condition
         ('Tulliniemi', 'self.wind_speed>=10 and self.wind_dir>=90 and self.wind_dir<=180'),
     ),
     ( # three star condition
         ('Tulliniemi', 'self.wind_speed>=12 and self.wind_dir>=95 and self.wind_dir<=170'),
     )
 ),
    ('Silveri', 
     ( # one star condition
         ('Tulliniemi', 'self.wind_speed>=8 and ( self.wind_dir>=260 or self.wind_dir<=20 )'),
     ),
     ( # two star condition
         ('Tulliniemi', 'self.wind_speed>=10 and self.wind_dir>=280 and self.wind_dir<=320'),
     )
 ),
    ('Veda', 
     ( # one star condition
         ('Tulliniemi', 'self.wind_speed>=8 and self.wind_dir>=110 and self.wind_dir<=260'),
     ),
     ( # two star condition
         ('Tulliniemi', 'self.wind_speed>=10 and self.wind_dir>=110 and self.wind_dir<=260'),
     ),
     ( # three star condition
         ('Tulliniemi', 'self.wind_speed>=12 and self.wind_dir>=160 and self.wind_dir<=230'),
     )
 ),
    ('4TT', 
     ( # one star condition
         ('Tulliniemi', 'self.wind_speed>=8 and self.wind_dir>=160 and self.wind_dir<=255'),
     ),
     ( # two star condition
         ('Tulliniemi', 'self.wind_speed>=10 and self.wind_dir>=160 and self.wind_dir<=240'),
     )
 ),
    ('Slaktis', 
     ( # one star condition
         ('Tulliniemi', 'self.wind_speed>=8 and self.wind_dir>=235 and self.wind_dir<=310'),
     )
 ),
    ('Yyteri', 
     ( # one star condition
         ('Tahkoluoto', 'self.wind_speed>=8 and self.wind_dir>=170 and self.wind_dir<=315'),
         ('yyteri', 'self.wind_speed>=5 and self.wind_dir>=170 and self.wind_dir<=315'),
     ),
     ( # two star condition
         ('Tahkoluoto', 'self.wind_speed>=9 and self.wind_dir>=210 and self.wind_dir<=280'),
         ('yyteri', 'self.wind_speed>=6 and self.wind_dir>=210 and self.wind_dir<=280'),
     ),
     ( # three star condition
         ('Tahkoluoto', 'self.wind_speed>=10 and self.wind_dir>=210 and self.wind_dir<=280'),
         ('yyteri', 'self.wind_speed>=8 and self.wind_dir>=210 and self.wind_dir<=280'),
     )
 ),
    ('Pollari', 
     ( # one star condition
         ('Tahkoluoto', 'self.wind_speed>=8 and self.wind_dir>=215 and self.wind_dir<=280'),
     ),
     ( # two star condition
         ('Tahkoluoto', 'self.wind_speed>=9 and self.wind_dir>=225 and self.wind_dir<=270'),
     ),
     ( # three star condition
         ('Tahkoluoto', 'self.wind_speed>=8 and self.wind_dir>=230 and self.wind_dir<=260'),
     )
 ),
]

#spots = []

ilmlurl = "http://ilmatieteenlaitos.fi/suomen-havainnot?p_p_id=stationstatusportlet_WAR_fmiwwwweatherportlets&p_r_p_1689542720_parameter=21&"
remlog = "http://www.remlog.com/cgi/tplast.pl?node="
yyteriUrl="http://www.purjelautaliitto.fi/yyteriweather/"
saapalveluUrl="http://www.saapalvelu.fi"
omasaaUrl="http://www.omasaa.fi"
windguruInfoUrl='https://beta.windguru.cz/station/'
windguruApiUrl='https://www.windguru.cz/int/wgsapi.php?q=station_data_current&'
holfuyApiUrl="http://holfuy.com/en/modules/mjso.php?"
holfuyInfoUrl="http://holfuy.com/en/data/114"
#ret={"wind_avg":2.72,"wind_max":4.85,"wind_min":1.16,"wind_direction":168.1,"temperature":15.1,"mslp":0,"rh":0,"datetime":"2014-06-28 20:31:35 EEST","unixtime":1403976695,"error_details":""}
#print(ret)
#exit()

def getUrl(url):
    f = urllib.request.urlopen(url)
    res = f.read()
    f.close()
    return res

#guruData = getUrl(windguruUrl + "&q=station_data_current&id_station=47")
#evalThis = guruData[2:len(guruData)-2].replace("null", "0")
#ret=eval(evalThis)
#print(ret)
#print("wind max", float(ret["wind_max"])/ms_to_knts)
#exit()


oldLimitMin = 100

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
        if string.printable.find(str(a[i])) >= 0:
            b = b+str(a[i])
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
        self.intemp = False
        self.inwind = False
        self.intempBox = 0
        self.inwindBox = 0
        self.intime = 0
        self.divLevel = 0
        self.row = -1
        self.column = -1
        self.text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            self.divLevel += 1
            if len(attrs) > 0 and attrs[0][0] == 'class' and attrs[0][1] == 'weather-box weather-box-thermometer':
                self.intempBox = self.divLevel
#                print(attrs[0][1], file=sys.stderr)
            if len(attrs) > 0 and attrs[0][0] == 'class' and attrs[0][1] == 'weather-box weather-box-wind':
                self.inwindBox = self.divLevel
#                print(attrs[0][1], file=sys.stderr)
            
    def handle_endtag(self, tag):
#            self.intemp = False
#            self.inwind = False
#            self.text = ""
        if tag == "div":
            if self.divLevel == self.intempBox:
                self.intempBox = 0
                self.intemp = False
            if self.divLevel == self.inwindBox:
                self.inwindBox = 0
            self.divLevel -= 1

    def handle_data(self, data):
        self.text = self.text + " " + data

        if self.intemp == 2:
            reg = re.search('([\-0-9]+[,\.]*[0-9]*)', data)
            if reg:
                self.temp = reg.group(1).replace(",", ".")
                self.intemp = 0
#                print("temp: ", self.temp, file=sys.stderr)

        if self.intemp and data == "Tll hetkell":
            self.intemp = 2
#            print(data, file=sys.stderr)
            
        if self.intempBox and data == "Lmptila":
            self.intemp = 1
#            print(data, file=sys.stderr)

        if self.inwind == 2:
            reg = re.search('([0-9]+[,\.]*[0-9]*) m/s', data)
            if reg:
                self.wind_max = reg.group(1).replace(",", ".")
#                print("wind_speed: ", self.wind_speed, file=sys.stderr)
                self.inwind = 1
                self.found = True

        if self.inwind == 3:
            reg = re.search('([0-9]+[,\.]*[0-9]*) m/s', data)
            if reg:
                self.wind_speed = reg.group(1).replace(",", ".")
#                print("wind_max: ", self.wind_max, file=sys.stderr)
                self.inwind = 1

        if self.inwind == 4:
            reg = re.search('\(([0-9]+)$', data)
            if reg:
                self.wind_dir = reg.group(1)
#                print("wind_dir: ", self.wind_dir, file=sys.stderr)
                self.inwind = 1

        if self.inwind == 1 and data == "Tuulen suunta ":
            self.inwind = 4

        if self.inwind == 1 and data.startswith("Keskituuli t"):
            self.inwind = 3

        if self.inwind == 1 and data == "Tuulen nopeus ":
            self.inwind = 2

        if self.inwindBox and data == "Tuuli":
            self.inwind = 1
            
        if self.intime == 2:
            reg = re.search(' ([0-9]+:[0-9]+)', data)
            if reg:
                self.time = reg.group(1)
#                print("time: ", self.time, file=sys.stderr)
                self.intime = 0

        if self.intime == 1 and data == "klo":
            self.intime = 2

        if data.startswith("Pivitetty"):
            self.intime = 1

        # if self.intable and self.intd:
        #     if self.text.startswith(" Lmptila"):
        #         self.intemp = True
        #     if self.text.startswith(" Tuuli"):
        #         self.intuuli = True
        #     if self.text.startswith(" Keskituuli t") and self.intuuli:
        #         self.found = True
        #         reg = re.search('([0-9]+\.[0-9]+) m/s', self.text)
        #         if reg:
        #             self.wind_speed = reg.group(1)
        #     if self.text.startswith(" Tuulen nopeus") and self.intuuli:
        #         reg = re.search('([0-9]+\.[0-9]+) m/s', self.text)
        #         if reg:
        #             self.wind_max = reg.group(1)
        #     if self.text.startswith(" Tuulen suunta") and self.intuuli:
        #         reg = re.search('10min.* \(([0-9]+)', self.text)
        #         if reg:
        #             self.wind_dir = reg.group(1)
        #     if self.text.startswith(" T ll  hetkell") and self.intemp:
        #         reg = re.search(' ([\-0-9]+\.[0-9])', self.text)
        #         if reg:
        #             self.temp = reg.group(1)
        # if self.text.startswith(" P ivittynyt viimeksi:") and self.inspan:
        #     reg = re.search(' ([0-9]+:[0-9]+)', self.text)
        #     if reg:
        #         self.time = reg.group(1)
                

#page = getUrl(yyteriUrl)
#parser = YyteriParser("")
#parser.feed(page)
#print(parser.time)
#print(parser.wind_dir)
#print(parser.wind_speed)
#print(parser.wind_max)
#exit()

class OmasaaParser(HTMLParser):
    
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
        self.intemp = False
        self.inwind = False
        self.inwinddir = False
        self.intime = 0
        self.text = ""

    def handle_starttag(self, tag, attrs):
        self.text = ''
        if tag == "span":
            if len(attrs) > 0 and attrs[0][0] == 'id' and attrs[0][1] == 'wind_force66':
                self.inwind = True
            if len(attrs) > 0 and attrs[0][0] == 'id' and attrs[0][1] == 'wdir_166':
                self.inwinddir = True
            if len(attrs) > 0 and attrs[0][0] == 'id' and attrs[0][1] == 'temp66':
                self.intemp = True
            if len(attrs) > 0 and attrs[0][0] == 'id' and attrs[0][1] == 'time66':
                self.intime = True

    def handle_endtag(self, tag):
        if tag == "span":
            self.inwind = False
            self.intemp = False
            self.inwinddir = False
            self.intime = False

    def handle_data(self, data):
        self.text = self.text + " " + data
        if self.inwind:
            self.wind_speed = float(self.text)
            self.wind_max = self.wind_speed
            self.found = True
        if self.inwinddir:
            self.wind_dir = float(self.text)
        if self.intemp:
            self.temp = float(self.text)
        if self.intime:
            self.time = self.text

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
        reg = re.search(b'([0-9]+:[0-9]+)[ \t]*Dir:[ \t]*([0-9]+)[ \t]*.*Low:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*Avg:[ \t]*([0-9\.]+)[ \t]*High:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*([-0-9\.]+)', self.text)
        if reg:
            self.time  = reg.group(1)
            self.wind_dir = reg.group(2)
            self.wind_low = reg.group(4)
            self.wind_speed = reg.group(5)
            self.wind_max = reg.group(7)
            self.temp = reg.group(8)
            self.found = True

class DataGather(object):
    
    def __init__(self, initData, info_url):
        if initData:
            self.name = initData[1]
        else:
            self.name = ''
        self.time = "00:00"
        self.wind_dir = 0
        self.wind_low = 0
        self.wind_speed = 0
        self.wind_max = 0
        self.temp = 0
        self.found = False
        self.info_url = info_url
        if len(initData) > 4:
            self.keli_ehto = initData[4]
        else:
            self.keli_ehto = ''

    def onkoKelia(self):
        return self.keli_ehto  and not self.oldTime() and eval(self.keli_ehto)

    def oldTime(self):
        print(self.time)
        if isinstance(self.time, str):
            hm = self.time.split(':')
        else:
            hm = self.time.split(b':')
        if len(hm) < 2:
            return False
        hr = int(hm[0])
        min = int(hm[1])
        old = False
        tm = time.time()
        t=time.localtime(tm)
        hour=t.tm_hour
        minute=t.tm_min
        if hour >= hr:
            old = hour * 60 + minute - (hr * 60 + min) > oldLimitMin
        else:
            old = 24*60 - hour * 60 + minute + (hr * 60 + min) > oldLimitMin    
#        if old:
#            print("old time: ", "hour", hour, "minute", minute, "station hour", hr, "station min", min, "limit", oldLimitMin, file=sys.stderr)
        return old

class YyteriGather(DataGather):

    def __init__(self, initData):
        self.page_url = yyteriUrl
        super(YyteriGather, self).__init__(initData, initData[2])

    def doGather(self):
        self.page = getUrl(self.page_url)
        self.parser = YyteriParser(self.info_url)
        self.parser.feed(self.page)
        if self.parser.found:
            self.found = True
            self.time = self.parser.time
            self.wind_dir = float(self.parser.wind_dir)
            self.wind_low = float(self.parser.wind_low)
            self.wind_speed = float(self.parser.wind_speed)
            self.wind_max = float(self.parser.wind_max)
            self.temp = float(self.parser.temp)

class RemlogGather(DataGather):

    def __init__(self, initData):
        self.page_url = remlog + initData[1]
        super(RemlogGather, self).__init__(initData, initData[2])

    def doGather(self):
        self.page = getUrl(self.page_url)
        self.parser = RemlogParser(self.info_url)
        self.parser.feed(self.page)
        self.parser.close()
        if self.parser.found:
            self.found = True
            self.time = self.parser.time
            self.wind_dir = float(self.parser.wind_dir)
            self.wind_low = float(self.parser.wind_low)
            self.wind_speed = float(self.parser.wind_speed)
            self.wind_max = float(self.parser.wind_max)
            self.temp = float(self.parser.temp)

class IlmlGather(DataGather):

    def __init__(self, initData):
        self.page_url = ilmlurl + initData[2]
        super(IlmlGather, self).__init__(initData, ilmlurl + initData[2])

    def doGather(self):
        self.page = getUrl(self.page_url)
        self.parser = ILMLParser(self.info_url)
        self.parser.feed(self.page)
        self.parser.close()
        if self.parser.found:
            self.found = True
            self.time = self.parser.parameterValues["time"]
            self.wind_dir = self.parser.parameterValues["wind_dir"]
            self.wind_speed = self.parser.parameterValues["wind_speed"]
            self.wind_max = self.parser.parameterValues["Puuska"]
            self.temp = self.parser.parameterValues["Lämpötila"]

class SaapalveluGather(DataGather):

    def __init__(self, initData):
        self.page_url = saapalveluUrl + initData[2]
        super(SaapalveluGather, self).__init__(initData, saapalveluUrl + initData[2])

    def doGather(self):
        self.page = getUrl(self.page_url)
        self.parser = SaapalveluParser(self.page_url)
        self.page = self.page.replace('sc\'+\'ript', 'script')
        self.parser.feed(onlyAscii(self.page))
        if self.parser.found:
            self.found = True
            self.time = self.parser.time
            self.wind_dir = float(self.parser.wind_dir)
            self.wind_low = float(self.parser.wind_low)
            self.wind_speed = float(self.parser.wind_speed)
            self.wind_max = float(self.parser.wind_max)
            self.temp = float(self.parser.temp)

class OmasaaGather(DataGather):

    def __init__(self, initData):
        self.page_url = omasaaUrl + initData[2]
        super(OmasaaGather, self).__init__(initData, omasaaUrl + initData[2])

    def doGather(self):
        self.page = getUrl(self.page_url)
        self.parser = OmasaaParser(self.page_url)
        self.parser.feed(onlyAscii(self.page))
        if self.parser.found:
            self.found = True
            self.time = self.parser.time
            self.wind_dir = float(self.parser.wind_dir)
            self.wind_low = float(self.parser.wind_low)
            self.wind_speed = float(self.parser.wind_speed)
            self.wind_max = float(self.parser.wind_max)
            self.temp = float(self.parser.temp)

class BwGather(DataGather):

    def __init__(self, initData):
        self.page_url = initData[2]
        super(BwGather, self).__init__(initData, initData[3])

    def doGather(self):
        self.parser = bwParser(self.info_url)
        self.parser.parse(self.page_url)
        if self.parser.found:
            self.found = True
            self.time = self.parser.time
            self.wind_dir = float(self.parser.wind_dir)
            self.wind_low = float(self.parser.wind_low)
            self.wind_speed = float(self.parser.wind_speed)
            self.wind_max = float(self.parser.wind_max)
            self.temp = float(self.parser.temp)

def myfloat(str):
    try:
        return float(str)
    except:
        return 'na'

class FmiBetaGather(DataGather):

    def __init__(self, initData):
        self.station = initData[2]
        super(FmiBetaGather, self).__init__(initData, ilmlurl + 'station=' + initData[2])

    def doGather(self):
        self.observations = fetch_data_lib.fetchDataNumDays(fmiApiKey, self.station, 0, 'winddirection,windspeedms,windgust,temperature')
        if len(self.observations) > 0:
            last = len(self.observations[0]) - 1
            while self.observations[0][last].lower() == "nan" and last-1 > 0:
                last = last - 2
            if last-1 < 0:
                return
            self.found = True
            tm = self.observations[0][last-1].split(',')
            self.time = tm[len(tm)-1]
            self.wind_dir = myfloat(self.observations[0][last])
            self.wind_speed = myfloat(self.observations[1][last])
            self.wind_max = myfloat(self.observations[2][last])
            self.temp = myfloat(self.observations[3][last])

class WindguruGather(DataGather):

    def __init__(self, initData):
        self.station = initData[2]
        stationId = re.search('id_station=([0-9]*)', initData[2])
        super(WindguruGather, self).__init__(initData, windguruInfoUrl + stationId.group(1))

    def doGather(self):
        self.observationJson = getUrl(windguruApiUrl + self.station)
#        print(self.observationJson, file=sys.stderr)
        try:
            self.observation = eval(self.observationJson.replace(b"null", b"0"))
            if len(self.observation) > 0:
                self.found = True
                self.wind_speed = round(float(self.observation["wind_avg"])/ms_to_knts,1)
                self.wind_max = round(float(self.observation["wind_max"])/ms_to_knts,1)
                self.wind_low = round(float(self.observation["wind_min"])/ms_to_knts,1)
                self.wind_dir = round(float(self.observation["wind_direction"]),1)
                self.temp = float(self.observation["temperature"])
                tmp = self.observation["datetime"].split(' ')[1].split(':')
                self.time = tmp[0] + ":" + tmp[1]
        except:
            print("Problems with data from WindGuru", self.observationJson, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self.found = False

class HolfuyGather(DataGather):

    def __init__(self, initData):
        self.station = initData[2]
        super(HolfuyGather, self).__init__(initData, holfuyInfoUrl)

    def doGather(self):
        try:
            self.observationJson = getUrl(holfuyApiUrl + self.station)
            self.observation = eval(self.observationJson.replace("\n", " ").replace("null", "0"))
            if len(self.observation) > 0:
                self.found = True
                self.wind_speed = round(float(self.observation["speed"]),1)
                self.wind_max = round(float(self.observation["gust"]),1)
                self.wind_dir = round(float(self.observation["dir"]),1)
                self.temp = float(self.observation["temperature"])
                try:
                    tmp = int(self.observation["updated"].split(' ')[0].replace("<b>", "").replace("</b>", ""))
                    tm = datetime.datetime.now() - timedelta(seconds=tmp)
                    self.time = str(tm.hour) + ":" + str(tm.minute)
                except:
                    tm = self.observation["updated"].split(' ')[1].split(":")
                    self.time = tm[0]+":"+tm[1]
        except:
            print("Problems with data from Holfui", self.observationJson, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self.found = False

def nameToVar(a):
    return a.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace('Å', 'A').replace('Ä', 'A').replace('Ö', 'O').replace('.', '')

nullStation = DataGather('', '')

# [ (spot, ( (station1, condition1), (station2, condition2) ), 
#          ( (station1, condition3), (station2, condition3) ), ) ]

def onkoSpotillaKelia(spot, S):
#    print("spot: ", spot, file=sys.stderr)
    stars = 0
    spotname = spot[0]
    for conditions in spot[1:]:
        add_star = False
        for station in conditions:
            if len(station) < 2:
                continue
            name = station[0]
#            print("name: ", name, file=sys.stderr)
            if name in S and S[name].found and not S[name].oldTime():
                condition = station[1]
                condition = condition.replace('self.', 'S["'+name+'"].')
                ret = eval(condition)
#                print(name, condition, ret, file=sys.stderr)
                if ret:
                    add_star = True
                else:
                    add_star = False
                    break
        if add_star:
            stars += 1
    return stars

def gatherAllStationData(_fmiApiKey):
    global fmiApiKey
    fmiApiKey = _fmiApiKey

    S = {} # stations to use when checking wind on spots
    res_list = []

    for v in stations:
        try:
            gatherer = eval(v[0] + "Gather(v)")
            gatherer.doGather()
            if gatherer.found:
                res_list.append(gatherer)
                S[nameToVar(gatherer.name)] = gatherer
            else:
                S[nameToVar(gatherer.name)] = nullStation
        except IOError:
            traceback.print_exc(file=sys.stderr)

    htmlCode = []

    if "SERVER_NAME" in os.environ:
        htmlCode.append('Content-Type: text/html\n')
        htmlCode.append('\n')
    htmlCode.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n')
    htmlCode.append('  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
    htmlCode.append('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">\n')
    htmlCode.append('  <head>\n')
    htmlCode.append('    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>\n')
    htmlCode.append('    <title>Tuulet</title>\n')
    htmlCode.append('    <style type="text/css">\n')
    htmlCode.append('    v\:* {\n')
    htmlCode.append('      behavior:url(#default#VML);\n')
    htmlCode.append('    }\n')
    htmlCode.append('body { margin:0;padding:0; color:#3D3D33; font:10px verdana,arial,sans-serif; line-height:1.4; text-align:left; } table {font:10px verdana, arial, sans-serif;border:0;text-align:left;}\n')
    htmlCode.append('table.lboardsnip { background-color:#fff;text-align:center;width:60px;font-size:9px;border-collapse:collapse;}\n')
    htmlCode.append('table.lboardsnip td, table.lboardsnip th { border:1px solid #999;padding:3px 1px; vertical-align:middle;}\n')
    htmlCode.append('table.lboardsnip tr.head th {background-color:#3D3D33;color:#CCCCC2;font-weight:normal;}\n')
    htmlCode.append('table.lboardsnip tr.odd {background-color:#CCCCC2;}\n')
    htmlCode.append('table.lboardsnip tr.even {background-color:#DCDCD2;}\n')
    htmlCode.append('table.lboardsnip tr.kelia {background-color:#D2F1D2;}\n')
    htmlCode.append('table.lboardsnip td.even {background-color:#CCCCC2;}\n')
    htmlCode.append('table.lboardsnip td.odd {background-color:#DCDCD2;}\n')
    htmlCode.append('table.lboardsnip td.kelia {background-color:#D2F1D2;}\n')
    htmlCode.append('table.lboardsnip tr.oldtime {color:#909090; background-color:#DCDCD2;}\n')
    htmlCode.append('table.lboardsnip tr.foot td {background-color:#AAAAA0;font-weight:normal;padding-left:4px;}\n')
    htmlCode.append('table.lboardsnip .lal {padding-left:4px;}\n')
    htmlCode.append('.larr {background:url(http://i.pga.com/pga/images/pgachampionship/img/icon_linkarrR.gif) no-repeat;padding-left:6px;display:inline;font-size:10px;font-weight:bold; }\n')
    htmlCode.append('.lal {text-align:left;}\n')
    htmlCode.append('a:link, a:visited, a:hover, a:active {color:#3D3D33;}\n')
    htmlCode.append('select {font-size:9px;}\n')
    htmlCode.append('option {font-size:9px;}\n')
    htmlCode.append('td {white-space:nowrap}\n')
    htmlCode.append('    </style>\n')
    htmlCode.append('<META HTTP-EQUIV="REFRESH" CONTENT="600">\n')
    htmlCode.append('    <script type="text/javascript" src="wind_data/sylvester.js">\n')
    htmlCode.append('    </script>\n')
    htmlCode.append('    <script type="text/javascript" src="wind_data/history_graph.js">\n')
    htmlCode.append('    </script>\n')
    htmlCode.append('    <script>\n')
    htmlCode.append('      window.onload = function(){\n')
    htmlCode.append('      setDataDir("wind_data/");\n')
    htmlCode.append('      initGraph(false);\n')
    htmlCode.append('      t1 = document.getElementById("wind_table");\n')
    htmlCode.append('      t2 = document.getElementById("spot_table");\n')
    htmlCode.append('      t2.style.width = "" + t1.offsetWidth + "px";\n')
    htmlCode.append('      };\n')
    htmlCode.append('    </script>\n')
    htmlCode.append('  </head>\n')

    htmlCode.append('<table  cellpadding="0" cellspacing="0">\n')
    htmlCode.append('  <tr>\n')
    htmlCode.append('    <td>\n')
    htmlCode.append('    <table id="wind_table" class="lboardsnip" cellpadding="0" cellspacing="0">\n')
    htmlCode.append('      <tbody>\n')
    htmlCode.append('	<tr class="head">\n')
    htmlCode.append('	  <th colspan="7"\n')
    htmlCode.append('	      style="padding-left: 4px;" align="left">\n')
    htmlCode.append('	    <div style="margin-top: 4px;">Tuulet (historiakäyrät klikkaamalla arvoja!)</div>\n')
    htmlCode.append('	  </th>\n')
    htmlCode.append('	</tr>\n')

    htmlCode.append('	<tr class="even">\n')
    htmlCode.append('	  <td class="lal"><b>Asema</b></td>\n')
    htmlCode.append('	  <td ><b>Aika</b></td>\n')
    htmlCode.append('	  <td ><b>Suunta</b></td>\n')
    htmlCode.append('	  <td ><b>Keski</b></td>\n')
    htmlCode.append('	  <td ><b>Max</b></td>\n')
    htmlCode.append('	  <td ><b>g%</b></td>\n')
    htmlCode.append('	  <td ><b>T</b></td>\n')
    htmlCode.append('	</tr>\n')

    odd = 1

    for l in res_list:
        htmlCode.append('	<tr class="')
        if l.oldTime():
            htmlCode.append("oldtime")
        else:
            if l.onkoKelia():
                htmlCode.append("kelia")
            elif odd:
                htmlCode.append("odd")
            else:
                htmlCode.append("even")
        htmlCode.append('">\n')
        odd = 1 - odd
        htmlCode.append('	  <td align="left"><a href="' + l.info_url + '">' + l.name + '</a></td>\n')
        htmlCode.append('	  <td>' + str(l.time) + '</td>\n')
        htmlCode.append('	  <td><a href="javascript:showStation(\'' + l.name + '\', 2)">' + str(l.wind_dir) + '</a></td>\n')
        htmlCode.append('	  <td><a href="javascript:showStation(\'' + l.name + '\', 0)">' + str(l.wind_speed) + '</a></td>\n')
        htmlCode.append('	  <td><a href="javascript:showStation(\'' + l.name + '\', 0)">' + str(l.wind_max) + '</a></td>\n')
        if l.wind_speed > 0:
            htmlCode.append('	  <td>'+ str(int((l.wind_max - l.wind_speed) / l.wind_speed * 100)) + '</td>\n')
        else:
            htmlCode.append('	  <td>0</td>\n')
        htmlCode.append('	  <td><a href="javascript:showStation(\'' + l.name + '\', 1)">' + str(l.temp) + '&deg;</a></td>\n')
        htmlCode.append('	</tr>\n')

    htmlCode.append('      </tbody>\n')
    htmlCode.append('    </table>\n')
    htmlCode.append('    </td>\n')
    htmlCode.append('    <td>\n')
    htmlCode.append('   <div id="station_name"></div>\n')
    htmlCode.append('  <canvas id="graphCanvas" width="550" height="260">\n')
    htmlCode.append('    </canvas>\n')
    htmlCode.append('   <select title="Select number of days to show" name="days" id="days"\n')
    htmlCode.append('   style="display:none" onchange="changeDays(this.value);">\n')
    htmlCode.append('      <option selected value="2">2 päivää</option>\n')
    htmlCode.append('      <option value="4">4 päivää</option>\n')
    htmlCode.append('      <option value="7">viikko</option>\n')
    htmlCode.append('      <option value="14">2 viikkoa</option>\n')
    htmlCode.append('      <option value="28">4 viikkoa</option>\n')
    htmlCode.append('    </select>\n')
    htmlCode.append('    <div id="debug"></div>\n')
    htmlCode.append('    </td>\n')
    htmlCode.append('  </tr>\n')
    htmlCode.append('    </table>\n')

    htmlCode.append('<table id="spot_table" class="lboardsnip" cellpadding="0" cellspacing="0">\n')
    htmlCode.append('      <tbody>\n')
    htmlCode.append('	<tr class="head">\n')
    htmlCode.append('	  <th colspan="4"\n')
    htmlCode.append('	      style="padding-left: 4px;" align="left">\n')
    htmlCode.append('	    <div style="margin-top: 4px;">Spotit</div>\n')
    htmlCode.append('	  </th>\n')
    htmlCode.append('	</tr>\n')

    for i, spot in zip(list(range(len(spots))), spots):
        if i % 2 == 0:
            htmlCode.append('<tr>\n')
        stars = onkoSpotillaKelia(spot, S)
        htmlCode.append('  <td width="25%" align="left" class="')
        if stars > 0:
            htmlCode.append("kelia")
        elif odd:
            htmlCode.append("odd")
        else:
            htmlCode.append("even",)
        htmlCode.append('">' + spot[0] + '</td>\n')
        htmlCode.append(' <td width="25%" class="')
        if stars > 0:
            htmlCode.append("kelia")
        elif odd:
            htmlCode.append("odd")
        else:
            htmlCode.append("even")
        htmlCode.append('">')
        if stars == 0:
            htmlCode.append('&#9785;')
        while stars > 0:
            stars -= 1
            htmlCode.append('&#9733;')
        htmlCode.append('</td>')
        if i % 2 == 1:
            htmlCode.append('</tr>')
            odd = 1 - odd
    htmlCode.append('	</table>')
    htmlCode.append('<br/><a href="forecasts.html">Ennusteet</a><br/><br/>')
    htmlCode.append('<a href="http://testbed.fmi.fi/history_browser.php?imgtype=wind&t=15&n=1">Testbed</a><br/><br/>')
    htmlCode.append('<a href="http://ilmatieteenlaitos.fi/sade-ja-pilvialueet/suomen-etelaosa">Sadetutka</a><br/><br/>')
    htmlCode.append('<a href="winds_ee.html">Eesti asemat</a><br/><br/>')
    htmlCode.append('Data <a href="http://ilmatieteenlaitos.fi/avoin-data">Ilmatieteen laitos</a><br/>' + str(datetime.datetime.now()))
    htmlCode.append(' </html>')
    return (htmlCode, res_list)


