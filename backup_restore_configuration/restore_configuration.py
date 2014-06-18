import json
import os
import requests
import sys

# Print usage if command line parameters not correctly provided
if len(sys.argv) != 5:
    print "Usage: python restore_configuration.py [account_hash] [host_hash] [scope_id] [infile]"
    sys.exit(1)

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else \
    'https://striketracker.highwinds.com'
ACCOUNT_HASH = sys.argv[1]
HOST_HASH = sys.argv[2]
SCOPE_ID = sys.argv[3]
INFILE = sys.argv[4]

# Grab the Oauth token
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Load configuration from file
with open(INFILE, 'r') as f:
    scope = json.load(f)

# Strip ids so our configuration will overwrite values currently set on the scope
for (key, policy) in scope.iteritems():
    if isinstance(policy, dict):
        if 'id' in policy:
            del policy['id']
    elif isinstance(policy, list):
        for policy_instance in policy:
            if 'id' in policy_instance:
                del policy_instance['id']

# Grab the current state of the scope and unset all types not in backup
scope_get = requests.get(
    STRIKETRACKER_URL + "/api/accounts/{account}/hosts/{host}/configuration/{scopeId}".format(
        account=ACCOUNT_HASH, host=HOST_HASH, scopeId=SCOPE_ID),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
print scope_get.json()
for type in scope_get.json().keys():
    if type not in scope:
        scope[type] = {}

# Restore scope's configuration
data = json.dumps(scope)
scope_put = requests.put(
    STRIKETRACKER_URL + "/api/accounts/{account}/hosts/{host}/configuration/{scopeId}".format(
        account=ACCOUNT_HASH, host=HOST_HASH, scopeId=SCOPE_ID),
    headers={
        "Authorization": "Bearer %s" % OAUTH_TOKEN,
        "Content-Type": "application/json"
    },
    data=data)
print 'Restoration %s\n%s' % (
    'succeeded' if scope_put.status_code == 200 else 'failed', scope_put.text)
sys.exit(0 if scope_put.status_code == 200 else 1)