import json
import os
import requests
import sys

# Print usage if command line parameters not correctly provided
if len(sys.argv) != 5:
    print "Usage: python backup_configuration.py [account_hash] [host_hash] [scope_id] [target_directory]"
    sys.exit(1)

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else \
    'https://striketracker.highwinds.com'
ACCOUNT_HASH = sys.argv[1]
HOST_HASH = sys.argv[2]
SCOPE_ID = sys.argv[3]
TARGET_DIR = sys.argv[4]

# Grab the Oauth token
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Back up scope configuration
scope_get = requests.get(
    STRIKETRACKER_URL + "/api/accounts/{account}/hosts/{host}/configuration/{scopeId}".format(
        account=ACCOUNT_HASH, host=HOST_HASH, scopeId=SCOPE_ID),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
if scope_get.status_code != 200:
    print "Could not fetch scope: \n%s" % scope_get.text
    sys.exit(1)
with open(os.path.join(TARGET_DIR, '{scope}.json'.format(scope=SCOPE_ID)), 'w') as f:
    json.dump(scope_get.json(), f, sort_keys=True, indent=4, separators=(',', ': '))