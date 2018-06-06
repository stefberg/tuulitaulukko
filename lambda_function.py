import boto3 
import urllib
import winds_lib

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

def lambda_handler(event, context):
#    windData = getUrl('http://dlarah.org/winds.html')
    print "starting update v2"
    windData = ""
    client = boto3.client('s3')
    obj = client.get_object(Bucket='windupdate', Key='fmi_api_key.txt')

    (htmlCode, list) = winds_lib.gatherAllStationData(obj['Body'].read())
    for l in htmlCode:
        windData += l + "\n"
    client.put_object(Body=windData, Bucket='windupdate', Key='winds.html', ACL='public-read', ContentType='text/html')
    print "update done"
    return 'Hello from Lambda'
