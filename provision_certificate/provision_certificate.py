import requests
import os
import sys
import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend

STRIKETRACKER_URL = os.environ['STRIKETRACKER_URL'] if 'STRIKETRACKER_URL' in os.environ else 'https://striketracker.highwinds.com'
if len(sys.argv) != 6:
    print "Usage: python provision_certificate.py [account_hash] [host name] [certificate] [key] [caBundle]"
    sys.exit()
PARENT_ACCOUNT = sys.argv[1]
HOST_NAME = sys.argv[2] # Friendly name for host in StrikeTracker
CERTIFICATE = sys.argv[3]  # SSL certificate file
KEY = sys.argv[4]  # SSL certificate key file
CA_BUNDLE = sys.argv[5]  # SSL certificate bundle file
OAUTH_TOKEN = os.environ['STRIKETRACKER_TOKEN']


# List certificates
def list_certificates():
    certificates_response = requests.get(
        STRIKETRACKER_URL + "/api/accounts/{accountHash}/certificates".format(accountHash=PARENT_ACCOUNT),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"})
    return certificates_response.json()


# Get certificate by hostname
def get_certificate(hostname):
    certificates = list_certificates()
    for certificate in certificates.get('list'):
        if certificate.get('commonName') == hostname:
            return certificate
    return None


# Construct certificate upload/update request body
def get_certificate_data():
    certificate_template = {"certificate": "", "key": "", "caBundle": ""}
    with open(CERTIFICATE, "rb") as f:
        certificate_template.update({'certificate': f.read().strip()})
    with open(KEY, "rb") as f:
        certificate_template.update({'key': f.read().strip()})
    with open(CA_BUNDLE, "rb") as f:
        certificate_template.update({'caBundle': f.read().strip()})
    return certificate_template

remoteCertificate = get_certificate(HOST_NAME)
localCertificateData = get_certificate_data()

if remoteCertificate is not None:
    certificateId = remoteCertificate.get('id')
    localCertificate = x509.load_pem_x509_certificate(localCertificateData.get('certificate'), default_backend())
    if int(localCertificate.serial_number) != int(remoteCertificate.get('certificateInformation').get('serialNumber')):
        print "Updating certificate for '{}' with new serialNumber '{}'".format(HOST_NAME, localCertificate.serial_number)
        update_certificate_responce = requests.put(
            STRIKETRACKER_URL + "/api/v1/accounts/{accountHash}/certificates/{certificateId}".format(accountHash=PARENT_ACCOUNT, certificateId=certificateId),
            headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
            data=json.dumps(localCertificateData)
        )
        update_certificate = update_certificate_responce.json()
        json.dump(update_certificate, sys.stdout, indent=4, separators=(',', ': '))
        print ""
    else:
        print "Local certificate for '{}' has same serialNumber as CDN, not updating".format(HOST_NAME)
else:
    print "Certificate not found in CDN"
    upload_certificate_responce = requests.post(
        STRIKETRACKER_URL + "/api/v1/accounts/{accountHash}/certificates".format(accountHash=PARENT_ACCOUNT),
        headers={"Authorization": "Bearer %s" % OAUTH_TOKEN, "Content-Type": "application/json"},
        data=json.dumps(localCertificateData)
    )
    update_certificate = upload_certificate_responce.json()
    json.dump(update_certificate, sys.stdout, indent=4, separators=(',', ': '))
    print ""
