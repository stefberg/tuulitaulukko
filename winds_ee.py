#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.dom.minidom
import urllib2
import time
import os
import sys
import winds_ee_lib

htmlCode = winds_ee_lib.gatherAllStationData()

for l in htmlCode:
    print l,
