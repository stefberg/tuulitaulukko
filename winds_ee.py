#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xml.dom.minidom
import urllib.request, urllib.error, urllib.parse
import time
import os
import sys
import winds_ee_lib

htmlCode = winds_ee_lib.gatherAllStationData()

for l in htmlCode:
    print(l, end=' ')
