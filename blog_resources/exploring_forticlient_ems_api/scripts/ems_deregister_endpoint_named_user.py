'''
ems_deregister_endpoint_named_user.py
Deregister endpoint using a user name, which is also the last seen user, on the endpoint using the FortiClient EMS API
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
user_name = "adkevin"
user_id = [] #This is a list, because a user can be associated with multiple endpoints
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

#Get user FortiClient ID with name match, then get endpoint ID with user ID match
for endpoint in response_decoded['data']['endpoints']:
    #If there is no recorded user on an endpoint the fct_users key does not exist
    try:
        for fct_user in endpoint['fct_users']:
            if fct_user['machine_user_name'] == user_name:
                #All user IDs get added to a list, because the ID can be associated with multiple endpoints
                user_id.append(fct_user['fct_user_id'])
        #Only if the user ID is the last seen user on the endpoint, the endpoint will be deregistered
        if endpoint['last_seen_fct_user_id'] in user_id:
            deregister_list.append(endpoint['device_id'])
            deregister_data = {"ids": deregister_list}
    except KeyError:
        continue

#Deregister endpoints that have the user name as the last seen user, which can be multiple
response = session.post(url=deregister_url, json=deregister_data, headers=change_headers, verify=False, timeout=30)
response_decoded = response.content.decode('utf-8')
print(response_decoded)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
