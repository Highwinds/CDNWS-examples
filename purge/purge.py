import getpass
import requests
import os
import sys
import json

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker3.highwinds.com'
if len(sys.argv) != 2:
    print "Usage: python provision_host.py [account_hash] < urls"
    sys.exit()
ACCOUNT_HASH = sys.argv[1]

# Build up purge batch
urls = []
for line in sys.stdin:
    urls.append({
        "url": line
    })
if len(urls) == 0:
    print "No urls to purge"
    sys.exit(1)
sys.stdin = open('/dev/tty')

# Log in and grab the Oauth token
auth = requests.post(
    HIGHWINDS_URL + "/auth/token",
    data={
    "grant_type": "password",
    "username": os.environ['STRIKETRACKER_USER'] if 'STRIKETRACKER_USER' in os.environ else raw_input('Username: ').strip(),
    "password": os.environ['STRIKETRACKER_PASSWORD'] if 'STRIKETRACKER_PASSWORD' in os.environ else getpass.getpass()
    }, headers={
    "Accept": "application/json"
    })
OAUTH_TOKEN = auth.json()['access_token']

# Purge urls
purge_response = requests.post(
    HIGHWINDS_URL + "/api/accounts/{accountHash}/purge".format(accountHash=ACCOUNT_HASH),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps({"list":urls}))
jobId = purge_response.json()['id']
print "Purge job %s submitted" % jobId

# Poll for status
progress = 0
while progress < 1:
    status_response = requests.get(
        HIGHWINDS_URL + "/api/accounts/{accountHash}/purge/{jobId}".format(
            accountHash=ACCOUNT_HASH,
            jobId=jobId),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
    progress = status_response.json()['progress']
    sys.stdout.write('\r[{0:50s}] {1}%'.format('#' * int(progress * 100.0 / 2), int(progress * 100)))
    sys.stdout.flush()
print "\nContent has been purged"