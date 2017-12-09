#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
from datetime import timedelta
import urllib
import string
import traceback
from HTMLParser import HTMLParser
import re
import os
import sys
import fetch_data_lib
import math

tm = time.time()
time=time.localtime(tm)
hour=time.tm_hour
minute=time.tm_min
ms_to_knts = (3.6 / 1.852)

entityChars = {"auml" : "ä", "ouml" : "ö", "aring" : "å", "nbsp" : " ", "Auml" : "Ä", "Ouml" : "Ö", "Aring" : "å"}

if os.uname()[1] == 'XXXX': # old station list kept here for a while
    stations = [ 
#             ("remlog", "leikosaari", "http://www.remlog.com/cgi/tplog.pl?node=leikosaari"),
#             ("remlog", "villinginluoto", "http://www.remlog.com/cgi/tplog.pl?node=villinginluoto"),
#             ("remlog", "apinalahti", "http://www.remlog.com/cgi/tplog.pl?node=apinalahti"),
#             ("remlog", "kalliosaari", "http://www.remlog.com/cgi/tplog.pl?node=kalliosaari"),
#             ("ilml", "Rankki", "station=2976&place=Kotka"), 
#             ("ilml", "Emäsalo", "station=2991&place=Porvoo"), 
#             ("ilml", "Kalbådagrund", "station=2987&place=Porvoo"),
#             ("fmibeta", "Eestiluoto", "101029"),
#             ("ilml", "Eestiluoto", "station=2930&place=Helsinki"),
#             ("ilml", "Kaisaniemi", "station=2978&place=Helsinki"),
#             ("fmibeta", "Harmaja", "100996"),
             ("ilml", "Harmaja", "station=2795&place=Helsinki"),
#             ("ilml", "Hel.Majakka", "station=2989&place=Helsinki"),
             ("saapalvelu", "koivusaari", "/helsinki/index.php"),
             ("bw", "eira", "http://eira.poista.net/lastWeather", "http://eira.poista.net/logWeather"),
             ("bw", "nuottaniemi", "http://eps.poista.net/lastWeather", "http://eps.poista.net/logWeather"),
#             ("fmibeta", "Bågaskär", "100969"),
             ("ilml", "Bågaskär", "station=2984&place=Inkoo"),
#             ("fmibeta", "Jussarö", "100965"),
             ("ilml", "Jussarö", "station=2757&place=Raasepori"),
#             ("remlog", "silversand", "http://www.remlog.com/tuuli/hanko.html"),
#             ("fmibeta", "Tulliniemi", "100946"),
             ("omasaa", "mulan", "/mulan/"),
             ("ilml", "Tulliniemi", "station=2746&place=Hanko"),
#             ("ilml", "Russarö", "station=2982&place=Hanko"),
#             ("ilml", "Isokari", "station=2964&place=Kustavi"),
#             ("ilml", "Rauma", "station=2761&place=Rauma"),
#             ("yyteri", "yyteri", "http://surfkeskus.dyndns.org/saa/"),
#             ("fmibeta", "Tahkoluoto", "101267"),
             ("ilml", "Tahkoluoto", "station=2751&place=Pori")
#             ("ilml", "Tankar", "station=2721&place=Kokkola"),
#             ("ilml", "Ulkokalla", "station=2907&place=Kalajoki")
             ]

else:
    stations = [ 
             ("FmiBeta", "Emäsalo", "101023"),
             ("FmiBeta", "Kalbådagrund", "101022"),
#             ("Remlog", "leikosaari", "http://www.remlog.com/cgi/tplog.pl?node=leikosaari"),
#             ("Remlog", "villinginluoto", "http://www.remlog.com/cgi/tplog.pl?node=villinginluoto"),
#             ("Remlog", "apinalahti", "http://www.remlog.com/cgi/tplog.pl?node=apinalahti", '', 'self.wind_speed>=5 and self.wind_dir>=75 and self.wind_dir<=290'),
             ("FmiBeta", "Eestiluoto", "101029", '', 'self.wind_speed>=7 and self.wind_dir>=75 and self.wind_dir<=290'),
             ("FmiBeta", "Hel.Majakka", "101003"),
             ("FmiBeta", "Harmaja", "100996", '', 'self.wind_speed>=7 and self.wind_dir>=180 and self.wind_dir<=240'),
             ("Windguru", "Laru", "id_station=47&password=contribyte", '', 'self.wind_speed>=6 and self.wind_dir>=180 and self.wind_dir<=240'),
#?({"return":"error","message":"Unauthorized API access!"});

#             ("Saapalvelu", "koivusaari", "/helsinki/index.php", '', 'self.wind_speed>=6 and self.wind_dir>=180 and self.wind_dir<=240'),
             ("Bw", "eira", "http://eira.poista.net/lastWeather", "http://eira.poista.net/logWeather", 'self.wind_max>=6 and self.wind_dir>=180+10 and self.wind_dir<=240+10'), # 10 deg off at the moment
#             ("Bw", "nuottaniemi", "http://eps.poista.net/lastWeather", "http://eps.poista.net/logWeather"),
             ("FmiBeta", "Bågaskär", "100969"),
             ("FmiBeta", "Jussarö", "100965"),
             ("Omasaa", "mulan", "/mulan/", '', 'self.wind_speed>=7 and ( self.wind_dir>=78 or self.wind_dir<=20 )'),
#             ("Remlog", "silversand", "http://www.remlog.com/tuuli/hanko.html"),
             ("FmiBeta", "Tulliniemi", "100946", '', 'self.wind_speed>=8 and self.wind_dir>=78 and self.wind_dir<=205'),
             ("FmiBeta", "Russarö", "100932"),
             ("Holfuy", "Bergön", "k=s114", '', ''),
             ("FmiBeta", "Vänö", "100945"),
             ("FmiBeta", "Utö", "100908"),
#             ("Yyteri", "yyteri", "http://www.purjelautaliitto.fi/yyteriweather/", '', 'self.wind_speed>=5 and self.wind_dir>=170 and self.wind_dir<=315'),
             ("FmiBeta", "Tahkoluoto", "101267", '', 'self.wind_speed>=8 and self.wind_dir>=170 and self.wind_dir<=315'),
             ("FmiBeta", "Tankar", "101661"),
             ("FmiBeta", "Ulkokalla", "101673"),
             ("FmiBeta", "Marjaniemi", "101784"),
             ("FmiBeta", "Vihreäsaari", "101794"),
             ]

#stations = [
    #("Ilml", "Kaisaniemi", "station=2978&place=Helsinki"),
#             ("Saapalvelu", "koivusaari", "/helsinki/index.php"),
#             ("Omasaa", "mulan", "/mulan/", '', 'self.wind_speed>=6 and self.wind_dir>=78 or self.wind_dir<=20'),
#             ("Bw", "eira", "http://eira.poista.net/lastWeather", "http://eira.poista.net/logWeather"),
#             ("FmiBeta", "Harmaja", "100996"),
#             ("FmiBeta", "Tulliniemi", "100946"),
#             ("Windguru", "laru", "id_station=47&password=contribyte"),
#             ]

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
         ('Tulliniemi', 'self.wind_speed>=8 and self.wind_dir>=235 and self.wind_dir<=275'),
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
windguruInfoUrl='https://beta.windguru.cz/station/47'
windguruApiUrl='https://www.windguru.cz/int/wgsapi.php?q=station_data_current&'
holfuyApiUrl="http://holfuy.com/en/modules/mjso.php?"
holfuyInfoUrl="http://holfuy.com/en/data/114"
#ret={"wind_avg":2.72,"wind_max":4.85,"wind_min":1.16,"wind_direction":168.1,"temperature":15.1,"mslp":0,"rh":0,"datetime":"2014-06-28 20:31:35 EEST","unixtime":1403976695,"error_details":""}
#print ret
#exit()

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

#guruData = getUrl(windguruUrl + "&q=station_data_current&id_station=47")
#evalThis = guruData[2:len(guruData)-2].replace("null", "0")
#ret=eval(evalThis)
#print ret
#print "wind max", float(ret["wind_max"])/ms_to_knts
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
#                print >>sys.stderr, attrs[0][1]
            if len(attrs) > 0 and attrs[0][0] == 'class' and attrs[0][1] == 'weather-box weather-box-wind':
                self.inwindBox = self.divLevel
#                print >>sys.stderr, attrs[0][1]
            
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
#                print >>sys.stderr, "temp: ", self.temp

        if self.intemp and data == "Tll hetkell":
            self.intemp = 2
#            print >>sys.stderr, data
            
        if self.intempBox and data == "Lmptila":
            self.intemp = 1
#            print >>sys.stderr, data

        if self.inwind == 2:
            reg = re.search('([0-9]+[,\.]*[0-9]*) m/s', data)
            if reg:
                self.wind_max = reg.group(1).replace(",", ".")
#                print >>sys.stderr, "wind_speed: ", self.wind_speed
                self.inwind = 1
                self.found = True

        if self.inwind == 3:
            reg = re.search('([0-9]+[,\.]*[0-9]*) m/s', data)
            if reg:
                self.wind_speed = reg.group(1).replace(",", ".")
#                print >>sys.stderr, "wind_max: ", self.wind_max
                self.inwind = 1

        if self.inwind == 4:
            reg = re.search('\(([0-9]+)$', data)
            if reg:
                self.wind_dir = reg.group(1)
#                print >>sys.stderr, "wind_dir: ", self.wind_dir
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
#                print >>sys.stderr, "time: ", self.time
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
#print parser.time
#print parser.wind_dir
#print parser.wind_speed
#print parser.wind_max
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
        reg = re.search('([0-9]+:[0-9]+)[ \t]*Dir:[ \t]*([0-9]+)[ \t]*.*Low:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*Avg:[ \t]*([0-9\.]+)[ \t]*High:[ \t]*([0-9\.]+)[ \t]*-[ \t]*([0-9\.]+)[ \t]*([-0-9\.]+)', self.text)
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
        hm = self.time.split(':')
        if len(hm) < 2:
            return False
        hr = int(hm[0])
        min = int(hm[1])
        old = False
        if hour >= hr:
            old = hour * 60 + minute - (hr * 60 + min) > oldLimitMin
        else:
            old = 24*60 - hour * 60 + minute + (hr * 60 + min) > oldLimitMin    
#        if old:
#            print >>sys.stderr, "old time: ", "hour", hour, "minute", minute, "station hour", hr, "station min", min, "limit", oldLimitMin
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
        self.observations = fetch_data_lib.fetchDataNumDays(self.station, 0, 'winddirection,windspeedms,windgust,temperature')
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
        super(WindguruGather, self).__init__(initData, windguruInfoUrl)

    def doGather(self):
        self.observationJson = getUrl(windguruApiUrl + self.station)
#        print >>sys.stderr, self.observationJson
        self.observation = eval(self.observationJson.replace("null", "0"))
        if len(self.observation) > 0:
            self.found = True
            self.wind_speed = round(float(self.observation["wind_avg"])/ms_to_knts,1)
            self.wind_max = round(float(self.observation["wind_max"])/ms_to_knts,1)
            self.wind_low = round(float(self.observation["wind_min"])/ms_to_knts,1)
            self.wind_dir = round(float(self.observation["wind_direction"]),1)
            self.temp = float(self.observation["temperature"])
            tmp = self.observation["datetime"].split(' ')[1].split(':')
            self.time = tmp[0] + ":" + tmp[1]

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
            print >>sys.stderr, "Problems with data from Holfui", self.observationJson
            traceback.print_exc(file=sys.stderr)
            self.found = False

def nameToVar(a):
    return a.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace('Å', 'A').replace('Ä', 'A').replace('Ö', 'O').replace('.', '')

nullStation = DataGather('', '')

# [ (spot, ( (station1, condition1), (station2, condition2) ), 
#          ( (station1, condition3), (station2, condition3) ), ) ]

def onkoSpotillaKelia(spot):
#    print >>sys.stderr, "spot: ", spot
    stars = 0
    spotname = spot[0]
    for conditions in spot[1:]:
        add_star = False
        for station in conditions:
            if len(station) < 2:
                continue
            name = station[0]
#            print >>sys.stderr, "name: ", name
            if name in S and S[name].found and not S[name].oldTime():
                condition = station[1]
                condition = condition.replace('self.', 'S["'+name+'"].')
                ret = eval(condition)
#                print >>sys.stderr, name, condition, ret
                if ret:
                    add_star = True
                else:
                    add_star = False
                    break
        if add_star:
            stars += 1
    return stars

S = {} # stations to use when checking wind on spots
list = []

for v in stations:
    try:
        gatherer = eval(v[0] + "Gather(v)")
        gatherer.doGather()
        if gatherer.found:
            list.append(gatherer)
            S[nameToVar(gatherer.name)] = gatherer
        else:
            S[nameToVar(gatherer.name)] = nullStation
    except IOError:
        traceback.print_exc(file=sys.stderr)

# test data
# S["Harmaja"].wind_speed = 11
# S["Harmaja"].wind_dir = 190
# S["Harmaja"].found = False
# S["eira"].time = "08:00"
# S["eira"].wind_max = 7
# S["eira"].wind_dir = 190
# S["Eestiluoto"].wind_speed = 8
# S["Eestiluoto"].wind_dir = 230
# S["Tulliniemi"].wind_speed = 12
# S["Tulliniemi"].wind_dir = 170
# S["Tahkoluoto"].wind_speed = 12
# S["Tahkoluoto"].wind_dir = 229

#print >>sys.stderr, "eira time", S["eira"].time

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
print 'table.lboardsnip { background-color:#fff;text-align:center;width:60px;font-size:9px;border-collapse:collapse;}'
print 'table.lboardsnip td, table.lboardsnip th { border:1px solid #999;padding:3px 1px; vertical-align:middle;}'
print 'table.lboardsnip tr.head th {background-color:#3D3D33;color:#CCCCC2;font-weight:normal;}'
print 'table.lboardsnip tr.odd {background-color:#CCCCC2;}'
print 'table.lboardsnip tr.even {background-color:#DCDCD2;}'
print 'table.lboardsnip tr.kelia {background-color:#D2F1D2;}'
print 'table.lboardsnip td.even {background-color:#CCCCC2;}'
print 'table.lboardsnip td.odd {background-color:#DCDCD2;}'
print 'table.lboardsnip td.kelia {background-color:#D2F1D2;}'
print 'table.lboardsnip tr.oldtime {color:#909090; background-color:#DCDCD2;}'
print 'table.lboardsnip tr.foot td {background-color:#AAAAA0;font-weight:normal;padding-left:4px;}'
print 'table.lboardsnip .lal {padding-left:4px;}'
print '.larr {background:url(http://i.pga.com/pga/images/pgachampionship/img/icon_linkarrR.gif) no-repeat;padding-left:6px;display:inline;font-size:10px;font-weight:bold; }'
print '.lal {text-align:left;}'
print 'a:link, a:visited, a:hover, a:active {color:#3D3D33;}'
#print 'a:hover {font-weight:bold;}'
print 'select {font-size:9px;}'
print 'option {font-size:9px;}'
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
print '      t1 = document.getElementById("wind_table");'
print '      t2 = document.getElementById("spot_table");'
print '      t2.style.width = "" + t1.offsetWidth + "px";'
print '      };'
print '    </script>'
print '  </head>'

print '<table  cellpadding="0" cellspacing="0">'
print '  <tr>'
print '    <td>'
print '    <table id="wind_table" class="lboardsnip" cellpadding="0" cellspacing="0">'
print '      <tbody>'
print '	<tr class="head">'
print '	  <th colspan="7"'
print '	      style="padding-left: 4px;" align="left">'
print '	    <div style="margin-top: 4px;">Tuulet (historiakäyrät klikkaamalla arvoja!)</div>'
print '	  </th>'
print '	</tr>'

print '	<tr class="even">'
print '	  <td class="lal"><b>Asema</b></td>'
print '	  <td ><b>Aika</b></td>'
print '	  <td ><b>Suunta</b></td>'
print '	  <td ><b>Keski</b></td>'
print '	  <td ><b>Max</b></td>'
print '	  <td ><b>g%</b></td>'
print '	  <td ><b>T</b></td>'
print '	</tr>'

odd = 1

for l in list:
    print '	<tr class="',
    if l.oldTime():
        print "oldtime",
    else:
        if l.onkoKelia():
            print "kelia",
        elif odd:
            print "odd",
        else:
            print "even",
    print '">'
    odd = 1 - odd
    print '	  <td align="left"><a href="' + l.info_url + '">' + l.name + '</a></td>'
    print '	  <td>' + str(l.time) + '</td>'
    print '	  <td><a href="javascript:showStation(\'' + l.name + '\', 2)">' + str(l.wind_dir) + '</a></td>'
    print '	  <td><a href="javascript:showStation(\'' + l.name + '\', 0)">' + str(l.wind_speed) + '</a></td>'
    print '	  <td><a href="javascript:showStation(\'' + l.name + '\', 0)">' + str(l.wind_max) + '</a></td>'
    if l.wind_speed > 0:
        print '	  <td>'+ str(int((l.wind_max - l.wind_speed) / l.wind_speed * 100)) + '</td>'
    else:
        print '	  <td>0</td>'
    print '	  <td><a href="javascript:showStation(\'' + l.name + '\', 1)">' + str(l.temp) + '&deg;</a></td>'
    print '	</tr>'

print '      </tbody>'
print '    </table>'
print '    </td>'
print '    <td>'
print '   <div id="station_name"></div>'
print '  <canvas id="graphCanvas" width="550" height="260">'
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

print '<table id="spot_table" class="lboardsnip" cellpadding="0" cellspacing="0">'
print '      <tbody>'
print '	<tr class="head">'
print '	  <th colspan="4"'
print '	      style="padding-left: 4px;" align="left">'
print '	    <div style="margin-top: 4px;">Spotit</div>'
print '	  </th>'
print '	</tr>'

for i, spot in zip(range(len(spots)), spots):
    if i % 2 == 0:
        print '<tr>'
    stars = onkoSpotillaKelia(spot)
    print '  <td width="25%" align="left" class="',
    if stars > 0:
        print "kelia",
    elif odd:
        print "odd",
    else:
        print "even",
    print '">', spot[0], '</td>'
    print ' <td width="25%" class="',
    if stars > 0:
        print "kelia",
    elif odd:
        print "odd",
    else:
        print "even",
    print '">'
    if stars == 0:
        print '&#9785;'
    while stars > 0:
        stars -= 1
        print '&#9733;'
    print '</td>'
    if i % 2 == 1:
        print '</tr>'
        odd = 1 - odd
print '	</table>'
print '<br/><a href="forecasts.html">Ennusteet</a><br/><br/>'
print '<a href="http://testbed.fmi.fi/history_browser.php?imgtype=wind&t=15&n=1">Testbed</a><br/><br/>'
print '<a href="http://ilmatieteenlaitos.fi/sade-ja-pilvialueet/suomen-etelaosa">Sadetutka</a><br/><br/>'
print '<a href="winds_ee.html">Eesti asemat</a><br/><br/>'
print 'Data <a href="http://ilmatieteenlaitos.fi/avoin-data">Ilmatieteen laitos</a><br/>', str(datetime.datetime.now())
print ' </html>'
#dir = 'ttt/'

if os.uname()[1] == 'kopsu.com':
    dir = '/home/webadmin/kopsu.com/html/wind_data/'
elif os.uname()[1] == 'Macintosh.local' or os.uname()[1] == 'Taru-MacBook-Pro-4.local':
    dir = './wind_data/'
else:
    dir = '/hsphere/local/home/saberg/dlarah.org/wind_data/'

stationsFile = 'stations.txt'

sf = open(dir + stationsFile, "w")
sf.write(str(time.tm_year) + "," + str(time.tm_yday))
sf.write("\n")
for l in list:
    sf.write(l.name)
    sf.write("\n")
    datafile = dir + l.name + "_" + str(time.tm_year) + "-" + str(time.tm_yday) + ".txt"
    lastline = []
    if os.path.exists(datafile):
        f = open(datafile, "r+")
        for line in f:
            if len(line.split(',')) > 6:
                lastline = line.split(',')
    else:
        f = open(datafile, "w")
    if len(lastline) == 0 or lastline[5] != l.time:
        f.write(str(time.tm_year) + ',' + str(time.tm_mon) + ',' + str(time.tm_mday) + ',' + str(time.tm_hour) + ',' + str(time.tm_min) + ',' + str(l.time) + ',' + str(l.wind_dir) + ',' + str(l.wind_low) + ',' + str(l.wind_speed) + ',' + str(l.wind_max) + ',' + str(l.temp).replace(',','.'))
        f.write("\n")
    f.close()
sf.close()
