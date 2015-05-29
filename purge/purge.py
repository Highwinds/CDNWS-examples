import requests
import os
import sys
import json

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else 'https://striketracker.highwinds.com'
if len(sys.argv) != 2:
    print "Usage: python purge.py [account_hash] < urls"
    sys.exit()
ACCOUNT_HASH = sys.argv[1]

# Grab the Oauth token
if 'STRIKETRACKER_TOKEN' not in os.environ:
    print "Please set the STRIKETRACKER_TOKEN environment variable to your token";
    sys.exit(1)
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Build up purge batch
urls = []
for line in sys.stdin:
    urls.append({
        "url": line
    })
if len(urls) == 0:
    print "No urls to purge"
    sys.exit(1)

# Purge urls
purge_response = requests.post(
    STRIKETRACKER_URL + "/api/accounts/{accountHash}/purge".format(accountHash=ACCOUNT_HASH),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps({"list":urls}))
jobId = purge_response.json()['id']
print "Purge job %s submitted" % jobId

# Poll for status
progress = 0
while progress < 1:
    status_response = requests.get(
        STRIKETRACKER_URL + "/api/accounts/{accountHash}/purge/{jobId}".format(
            accountHash=ACCOUNT_HASH,
            jobId=jobId),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
    progress = status_response.json()['progress']
    sys.stdout.write('\r[{0:50s}] {1}%'.format('#' * int(progress * 100.0 / 2), int(progress * 100)))
    sys.stdout.flush()
print "\nContent has been purged"