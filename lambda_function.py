import boto3 
import winds_lib
import time
import os

def updateStationsFile(client, list):
    stationsData = str(time.tm_year) + "," + str(time.tm_yday) + "\n"
    for l in list:
        stationsData += l.name + "\n"
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
