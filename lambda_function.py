import boto3 
import urllib

def getUrl(url):
    f = urllib.urlopen(url)
    res = f.read()
    f.close()
    return res

def lambda_handler(event, context):
    # TODO implement
    print "starting update v2"
    #windData = b'<html>New data from lambda</html>'
    windData = getUrl('http://dlarah.org/winds.html')
    client = boto3.client('s3')
    client.put_object(Body=windData, Bucket='windupdate', Key='winds.html', ACL='public-read', ContentType='text/html')
    print "update done"
    return 'Hello from Lambda'
