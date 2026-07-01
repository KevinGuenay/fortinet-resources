'''
ems_get_endpoint_data.py
Get endpoint data and ID for named endpoint using the FortiClient EMS API
'''

import json
import requests

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Disable warnings
requests.urllib3.disable_warnings()

#Set some variables for the API
ems_server = '192.168.1.208'
endpoint_name = "WIN11-CLIENT"

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
endpoints_url = f'{api_url_prefix}/endpoints/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get endpoint data
response = session.get(url=endpoints_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))
print(response_decoded)

#Get endpoint ID with name match
for endpoint in response_decoded['data']['endpoints']:
    if endpoint['name'] == endpoint_name:
        print(f"Endpoint ID for {endpoint_name}: {endpoint['device_id']}")

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
