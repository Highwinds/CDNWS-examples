import getpass
import requests
import os
import sys
import json

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker3.highwinds.com'
if len(sys.argv) != 3:
    print "Usage: python provision_account.py [parent_account_hash] [account name]"
PARENT_ACCOUNT = sys.argv[1]
ACCOUNT_NAME = sys.argv[2]

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
account = {
    "services": [40],  # Enable Global on this account by default
    "accountName": ACCOUNT_NAME,
    "supportEmailAddress": "qa@highwinds.com",
    "billingAccountNumber": "1234",
    "accountStatus": "ACTIVATED",
    "subAccountCreationEnabled": True,
    "maximumDirectSubAccounts": 10,
    "billingContact": {
        "firstName": "QA",
        "lastName": "TEST",
        "email": "qa@highwinds.com",
        "phone": "9",
        "address":{
            "line1":"807 W. Morse Boulevard",
            "line2":"Suite 101",
            "city":"Winter Park",
            "state":"FL",
            "postalCode":"32789",
            "country":"USA"
        }
    },
    "primaryContact": {
        "firstName": "QA",
        "lastName": "TEST",
        "email": "qa@highwinds.com",
        "phone": "9"
    },
    "technicalContact": {
        "firstName": "QA",
        "lastName": "TEST",
        "email": "qa@highwinds.com",
        "phone": "9"
    },
    "trial": False,
    "reseller": False
}

# Create the new account
account_response = requests.post(
    HIGHWINDS_URL + "/api/accounts/{accountHash}".format(accountHash=PARENT_ACCOUNT),
    headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
    data=json.dumps(account))
json.dump(account_response.json(), sys.stdout, indent=4, separators=(',', ': '))
print ""