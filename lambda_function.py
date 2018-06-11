import boto3 
import winds_lib
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
        try:
            obj = client.get_object(Bucket='windupdate', Key=datafile)
            data = obj['Body'].read()
        except:
            print "new data", datafile
        data += str(timeObj.tm_year) + ',' + str(timeObj.tm_mon) + ',' + str(timeObj.tm_mday) + ',' + str(timeObj.tm_hour) + ',' + str(timeObj.tm_min) + ',' + str(l.time) + ',' + str(l.wind_dir) + ',' + str(l.wind_low) + ',' + str(l.wind_speed) + ',' + str(l.wind_max) + ',' + str(l.temp).replace(',','.') + "\n"
        client.put_object(Body=data, Bucket='windupdate', Key=datafile, ACL='public-read', ContentType='text/plain;charset=utf-8')
        
    client.put_object(Body=stationsData, Bucket='windupdate', Key='wind_data/stations.txt', ACL='public-read', ContentType='text/plain;charset=utf-8')

def lambda_handler(event, context):
    os.environ["TZ"] = "Europe/Helsinki"
    time.tzset()
    print "starting update"
    windData = ""
    client = boto3.client('s3')
    obj = client.get_object(Bucket='windupdate', Key='fmi_api_key.txt')

    (htmlCode, list) = winds_lib.gatherAllStationData(obj['Body'].read())
    for l in htmlCode:
        windData += l + "\n"
    client.put_object(Body=windData, Bucket='windupdate', Key='winds.html', ACL='public-read', ContentType='text/html;charset=utf-8')
    print "wind update done"
    updateStationsFile(client, list)
    print "stations file update done"
    return 'OK'
