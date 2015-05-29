import getpass
import requests
import os
import sys

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else 'https://striketracker.highwinds.com'
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']

# Grab the currently authenticated user
me = requests.get(
	STRIKETRACKER_URL + "/api/users/me",
	headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
user = me.json()

# Grab this user's account's hosts
hosts = requests.get(
	STRIKETRACKER_URL + "/api/accounts/{accountHash}/hosts?recursive=true".format(accountHash=user['accountHash']),
	headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})

# Print list of hosts along with an indicator of whether CDS is enabled
print "Hash    \tCDS\tName\t"
for host in hosts.json()['list']:
	CDS_enabled = False
	for service in host['services']:
		if 'CDS' in service['name']:
			CDS_enabled = True
	print "{hash}\t{CDS}\t{name}".format(
		hash=host['hashCode'], CDS=CDS_enabled, name=host['name'])