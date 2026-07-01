'''
ems_deregister_endpoints.py
Deregister named endpoint(s) or IDs using the FortiClient EMS API
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
#Add the names of endpoints to this list
endpoint_names_list = ["WIN11-CLIENT", "FCXLAB"]
#Add known endpoint IDs you want to deregister to this list
deregister_list = []

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
endpoints_url = f'{api_url_prefix}/endpoints/index'
deregister_url = f'{api_url_prefix}/clients/deregister'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}
deregister_data = {}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

response = session.get(url=endpoints_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

#Get endpoint ID with name match and add to deregister list, then format data for API call
for endpoint in response_decoded['data']['endpoints']:
    if endpoint['name'] in endpoint_names_list:
        deregister_list.append(endpoint['device_id'])
        deregister_data = {"ids": deregister_list}

#Deregister endpoint(s)
session.post(url=deregister_url, json=deregister_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
