#!/usr/bin/python
# -*- coding: utf-8 -*-

import winds_lib

(htmlCode, list) = winds_lib.gatherAllStationData()
for l in htmlCode:
    print l,
winds_lib.updateStationsFile(list)
