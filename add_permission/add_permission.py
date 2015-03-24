import getpass
import requests
import os
import sys
import json

HIGHWINDS_URL = os.environ['HIGHWINDS_URL'] if 'HIGHWINDS_URL' in os.environ else 'https://striketracker3.highwinds.com'
if len(sys.argv) != 3:
    print "Usage: python add_permission.py [account hash] [userId]"
    sys.exit()
PARENT_ACCOUNT = sys.argv[1]
USERID = sys.argv[2] # Integer ID for user that is to be updated

with open('%s_%s.txt' % (PARENT_ACCOUNT, USERID), 'w') as log:

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

    # Get user
    get_response = requests.get(
        HIGHWINDS_URL + "/api/accounts/{accountHash}/users/{userId}".format(
            accountHash=PARENT_ACCOUNT,
            userId=USERID),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"})
    user = get_response.json()
    if user['userType'] != 'Normal':
        log.write("User is of type %s" % user['userType'])
        sys.exit(1)
    log.write("BEFORE:")
    json.dump(user, log, indent=4, separators=(',', ': '))
    phone = user['phone'] or '9'
    if user['roles']['userAccount']['content'] == 'EDIT':
        log.write("\nAlready has CONTENT EDIT\n\n\n")
        sys.exit(1)

    # Add content edit permission to a user so they can log into FTP
    update_response = requests.put(
        HIGHWINDS_URL + "/api/accounts/{accountHash}/users/{userId}".format(
            accountHash=PARENT_ACCOUNT,
            userId=USERID),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
        data=json.dumps({
            "phone": phone,
            "roles": {
                "userAccount": {
                    "content": "EDIT"
                }
            }
        }))
    user_after = update_response.json()
    log.write("\n\nAFTER:")
    json.dump(user_after, log, indent=4, separators=(',', ': '))
    log.write("\n\n\n")