from datetime import datetime, timedelta
from urllib import urlencode
import csv
import getpass
import os
import requests
import sys

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ \
    else 'https://striketracker.highwinds.com'
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Set up CSV writer
writer = csv.writer(sys.stdout, delimiter="\t")

# Grab the currently authenticated user
me = requests.get(
    STRIKETRACKER_URL + "/api/users/me",
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
user = me.json()

# Grab hourly data for the past 24 hours
end_date = datetime.utcnow()
start_date = end_date - timedelta(hours=24)

analytics = requests.get(
    STRIKETRACKER_URL + "/api/accounts/{accountHash}/analytics/transfer?{qs}".format(
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