import getpass
import requests
import os
import sys
import json

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else 'https://striketracker.highwinds.com'
if len(sys.argv) != 4:
    print "Usage: python modify_policies.py [account_hash] [host_hash] [scope_id]"
    sys.exit()
PARENT_ACCOUNT = sys.argv[1]
HOST = sys.argv[2] # Host hash
SCOPE_ID = sys.argv[3] # Scope id which you want to edit
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

configuration = {
    "dynamicContent": {
        "queryParams": "start,end"
    },
    "compression": {
        "gzip": "css,html"
    }
}

# Add policies
host_response = requests.put(
    STRIKETRACKER_URL + "/api/accounts/{accountHash}/hosts/{host}/configuration/{scope}".format(
        accountHash=PARENT_ACCOUNT,
        host=HOST,
        scope=SCOPE_ID
    ),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps(configuration))
host = host_response.json()
json.dump(host, sys.stdout, indent=4, separators=(',', ': '))
print ""

# Delete dynamicContent policy
host_response = requests.put(
    STRIKETRACKER_URL + "/api/accounts/{accountHash}/hosts/{host}/configuration/{scope}".format(
        accountHash=PARENT_ACCOUNT,
        host=HOST,
        scope=SCOPE_ID
    ),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps({
        "compression": {}
    }))
host = host_response.json()
json.dump(host, sys.stdout, indent=4, separators=(',', ': '))
print ""