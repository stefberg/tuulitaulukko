import boto3 
import winds_lib
import winds_ee_lib
import time
import os

def updateStationsFile(client, list):
    tm = time.time()
    timeObj=time.localtime(tm)
    stationsData = str(timeObj.tm_year) + "," + str(timeObj.tm_yday) + "\n"

    for l in list:
        stationsData += l.name + "\n"
        datafile = 'wind_data/' + l.name + "_" + str(timeObj.tm_year) + "-" + str(timeObj.tm_yday) + ".txt"
        data = ''
        lastline = ''
        try:
            obj = client.get_object(Bucket='dlarah.org', Key=datafile)
            data = obj['Body'].read()
            lines = data.split("\n")
            if len(lines) > 1:
                lastline = lines[len(lines)-2]
        except:
            print "new data", datafile
        if len(lastline) == 0 or lastline[5] != l.time:
            data += str(timeObj.tm_year) + ',' + str(timeObj.tm_mon) + ',' + str(timeObj.tm_mday) + ',' + str(timeObj.tm_hour) + ',' + str(timeObj.tm_min) + ',' + str(l.time) + ',' + str(l.wind_dir) + ',' + str(l.wind_low) + ',' + str(l.wind_speed) + ',' + str(l.wind_max) + ',' + str(l.temp).replace(',','.') + "\n"
            client.put_object(Body=data, Bucket='dlarah.org', Key=datafile, ACL='public-read', ContentType='text/plain;charset=utf-8')
        else:
            print "duplicate line not added", lastline, l
        
    client.put_object(Body=stationsData, Bucket='dlarah.org', Key='wind_data/stations.txt', ACL='public-read', ContentType='text/plain;charset=utf-8')

def lambda_handler(event, context):
    os.environ["TZ"] = "Europe/Helsinki"
    time.tzset()
    print "starting update"
    windData = ""
    client = boto3.client('s3')
    obj = client.get_object(Bucket='dlarah.org', Key='fmi_api_key.txt')

    (htmlCode, list) = winds_lib.gatherAllStationData(obj['Body'].read())
    for l in htmlCode:
        windData += l + "\n"
    client.put_object(Body=windData, Bucket='dlarah.org', Key='winds.html', ACL='public-read', ContentType='text/html;charset=utf-8')
    print "wind update done"
    updateStationsFile(client, list)
    print "stations file update done"

    print "fetching data for eesti stations"
    htmlCode = winds_ee_lib.gatherAllStationData()
    windData = ""
    for l in htmlCode:
        windData += l + "\n"
    client.put_object(Body=windData, Bucket='dlarah.org', Key='winds_ee.html', ACL='public-read', ContentType='text/html;charset=utf-8')
    print "wind update for ee done"
    return 'OK'
