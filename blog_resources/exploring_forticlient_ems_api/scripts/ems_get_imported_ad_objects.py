'''
ems_get_imported_ad_objects.py
Get imported groups of AD server using the FortiClient EMS API
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
idp_name = "ad.labdomain.com"

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
idps_url = f'{api_url_prefix}/idps/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get authentication servers data
response = session.get(url=idps_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

#Get imported OUs from IDP
for idp in response_decoded['data']:
    if idp['domain_info']['name'] == idp_name:
        idp_id = idp['domain_info']['guid']
        idp_ous_url = f'{api_url_prefix}/idps/adfs/{idp_id}/imported_ous'
        response = session.get(url=idp_ous_url, headers=api_headers, verify=False, timeout=30)
        response_decoded = json.loads(response.content.decode('utf-8'))
        print(response_decoded['data']['group_containers'])

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
