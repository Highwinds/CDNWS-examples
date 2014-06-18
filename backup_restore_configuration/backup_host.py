import os
import shlex
import requests
import subprocess
import sys

# Print usage if command line parameters not correctly provided
if len(sys.argv) > 4 or len(sys.argv) < 3:
    print "Usage: python backup_configuration.py [account_hash] [host_hash] {target_directory}"
    sys.exit(1)

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else \
    'https://striketracker.highwinds.com'
ACCOUNT_HASH = sys.argv[1]
HOST_HASH = sys.argv[2]
TARGET_DIR = sys.argv[3] if len(sys.argv) == 4 else os.getcwd()

# Grab the Oauth token
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Fetch selected host
host_get = requests.get(
    STRIKETRACKER_URL + "/api/accounts/{account}/hosts/{host}".format(
        account=ACCOUNT_HASH, host=HOST_HASH),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
host = host_get.json()
sys.stdout.write("Backing up configuration for %s..." % host['name'])
sys.stdout.flush()

# Fetch all configuration scopes
scopes_get = requests.get(
    STRIKETRACKER_URL + "/api/accounts/{account}/hosts/{host}/configuration/scopes".format(
        account=ACCOUNT_HASH, host=HOST_HASH),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
scopes = scopes_get.json()['list']

for scope in scopes:

    # Back up each scope
    subprocess.call(shlex.split(
        'python backup_configuration.py %s %s %s %s' % (
            ACCOUNT_HASH, HOST_HASH, scope['id'], TARGET_DIR)))

    sys.stdout.write(".")
    sys.stdout.flush()

sys.stdout.write(" Done!\n")
