'''
ems_get_policy.py
Get all policy data and ID for named policy using the FortiClient EMS API
'''

import json
import requests

#Disable warnings
requests.urllib3.disable_warnings()

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Set some variables for the API
ems_server = '192.168.1.208'
policy_name = 'POLICY_API'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
policy_get_url = f'{api_url_prefix}/endpoint_policies/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {
    "Content-type": "application/json",
    "Referer": f"https://{ems_server}", 
    "X-CSRFToken": f"{session.cookies["csrftoken"]}"
}

#Get policies
response = session.get(url=policy_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))
print(response_decoded)

#Print ID for a named policy
for policy in response_decoded['data']:
    if policy['name'] == policy_name:
        print(f"Policy ID for {policy_name}: {policy['id']}")

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
