from datetime import datetime, timedelta
from urllib import urlencode
import csv
import getpass
import os
import requests
import sys

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ \
    else 'https://striketracker.highwinds.com'

# Set up CSV writer
writer = csv.writer(sys.stdout, delimiter="\t")

# Log in and grad the Oauth token
auth = requests.post(
    HIGHWINDS_URL + "/auth/token",
    data={
        "grant_type": "password",
        "username": raw_input('Username: ').strip(),
        "password": getpass.getpass()
    }, headers={
        "Accept": "application/json"
    })
try:
    OAUTH_TOKEN = auth.json()['access_token']
except ValueError:
    print "Could not log in"
    sys.exit(1)

# Grab the currently authenticated user
me = requests.get(
    HIGHWINDS_URL + "/api/users/me",
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
user = me.json()

# Grab hourly data for the past 24 hours
end_date = datetime.utcnow()
start_date = end_date - timedelta(hours=24)

analytics = requests.get(
    HIGHWINDS_URL + "/api/accounts/{accountHash}/analytics/transfer?{qs}".format(
        accountHash=user['accountHash'],
        qs=urlencode({
            "startDate": start_date.strftime('%Y-%m-%dT%H:00:00Z'),
            "endDate": end_date.strftime('%Y-%m-%dT%H:00:00Z'),
            "granularity": "PT1H",
            "platforms": "3,34"  # CDS and SDS
        })
        ), headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
series = analytics.json()['series'][0]

# Print list of hosts along with an indicator of whether CDS is enabled
writer.writerow(['Time'.ljust(19), 'Total Requests', 'Total Transfer'])
xfer_key = series['metrics'].index('xferUsedTotalMB')
requests_key = series['metrics'].index('requestsCountTotal')
for row in series['data']:
    writer.writerow([
        # Convert javascript timestamp to ISO datetime
        datetime.fromtimestamp(int(row[0]) / 1000)\
            .strftime('%Y-%m-%d %H:%M:%S'),

        # Print out requests
        row[requests_key],

        # Print out transfer
        row[xfer_key]
    ])