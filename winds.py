#!/usr/bin/python
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
            dir = '/hsphere/local/home/saberg/winds/'
        api_key_file = dir + 'fmi_api_key.txt'
        #print os.uname()[1]
        #print "APIKEY file", api_key_file
        f = open(api_key_file, "r")
        apikey = f.read();
        apikey = apikey.replace('\n', '')
        f.close()
    return apikey

os.environ["TZ"] = "Europe/Helsinki"
time.tzset()

(htmlCode, list) = winds_lib.gatherAllStationData(getApiKey())
for l in htmlCode:
    print l,
winds_lib.updateStationsFile(list)
