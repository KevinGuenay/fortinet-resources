'''
ems_fgt_authorization_share_clients.py
Authorize a FortiGate and set properties on it using the FortiClient EMS API
'''

import requests

#Disable warnings
requests.urllib3.disable_warnings()

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Set some variables for the API
ems_server = '192.168.1.208'
fgt_serial = 'FGT70GSERIAL'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
fgt_authorization_url = f'{api_url_prefix}/client_certificates/set'
fgt_properties_url = f'{api_url_prefix}/fabric_device_auth/{fgt_serial}/update'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}
fgt_authorization_data = {"filters": {"management_mode": "standalone", "cns": [f"{fgt_serial}"]}, "properties": {"authorized": True}}

#share_mode 0 is "Only share FortiClients connected to this fabric device (Recommended)"
#share_mode 1 is "Share all FortiClients"
#share_tag_types 1 is "Security Posture Tags", 2 is "Outbreak Tags", 3 is "Classification Tags", 4 is "Fabric Tags"
fgt_properties_data = {"share_mode":1,"selected_cn_list":[],"share_tag_types":[1],"alias":"FGT-EMSAPI"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Authorize the FortiGate and set properties
session.patch(url=fgt_authorization_url, json=fgt_authorization_data, headers=change_headers, verify=False, timeout=30)
session.patch(url=fgt_properties_url, json=fgt_properties_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
