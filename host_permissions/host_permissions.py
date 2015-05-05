import getpass
import requests
import os
import sys

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker.highwinds.com'

# Log in and grab the Oauth token
auth = requests.post(
	HIGHWINDS_URL + "/auth/token",
	data={
		"grant_type": "password",
		"username": raw_input('Username: ').strip(),
		"password": getpass.getpass()
	}, headers={
		"Accept": "application/json"
	})
OAUTH_TOKEN = auth.json()['access_token']

# Grab the currently authenticated user
me = requests.get(
	HIGHWINDS_URL + "/api/users/me",
	headers={"Authorization": "Bearer %s" % OAUTH_TOKEN})
user = me.json()

# Grab this user's account's hosts
hosts = requests.get(
	HIGHWINDS_URL + "/api/accounts/{accountHash}/hosts?recursive=true".format(accountHash=user['accountHash']),
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