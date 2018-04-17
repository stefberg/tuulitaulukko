#!/bin/sh

cp winds.py fetch_data_lib.py /var/www/cgi-bin/
cp forecasts.html /var/www/html
cp -r wind_data /var/www/html
# crontab entry
#0,5,10,15,20,25,30,35,40,45,50,55 * * * * /home/ec2-user/tuulitaulukko/winds
