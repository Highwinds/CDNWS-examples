import getpass
import requests
import os
import sys
import json

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker3.highwinds.com'
if len(sys.argv) != 4:
    print "Usage: python provision_host.py [account_hash] [host name] [virtualhost]"
    sys.exit()
PARENT_ACCOUNT = sys.argv[1]
HOST_NAME = sys.argv[2] # Friendly name for host in StrikeTracker
VIRTUALHOST = sys.argv[3]  # Customer-facing url

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
host_data = {
    "services": [40],  # Enable Global on this host by default
    "name": HOST_NAME
}

# Create the new host
host_response = requests.post(
    HIGHWINDS_URL + "/api/accounts/{accountHash}/hosts".format(accountHash=PARENT_ACCOUNT),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps(host_data))
host = host_response.json()
json.dump(host, sys.stdout, indent=4, separators=(',', ': '))
print ""

# Create a hostname at CDS root
scope_id = None
for scope in host['scopes']:
    if scope['platform'] == 'CDS' and scope['path'] == '/':
        scope_id = scope['id']
if scope_id is None:
    print "Could not find CDS root"
    sys.exit(1)
scope_data = {
    'hostname': [
        {
            'domain': VIRTUALHOST
        }
    ]
}
scope_response = requests.put(
    HIGHWINDS_URL + "/api/accounts/{accountHash}/hosts/{hostHash}/configuration/{scopeId}".format(
        accountHash=PARENT_ACCOUNT,
        hostHash=host['hashCode'],
        scopeId=scope_id),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps(scope_data))
scope = scope_response.json()
json.dump(scope, sys.stdout, indent=4, separators=(',', ': '))
print ""