import getpass
import requests
import os
import sys
import json

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker3.highwinds.com'
if len(sys.argv) != 3:
    print "Usage: python provision_host.py [account_hash] [host name]"
PARENT_ACCOUNT = sys.argv[1]
HOST_NAME = sys.argv[2]

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

# Gather relevant information
host = {
    "services": [41],  # Enable Global Premium on this host by default
    "name": HOST_NAME
}

# Create the new host
host_response = requests.post(
    HIGHWINDS_URL + "/api/accounts/{accountHash}/hosts".format(accountHash=PARENT_ACCOUNT),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps(host))
json.dump(host_response.json(), sys.stdout, indent=4, separators=(',', ': '))
print ""