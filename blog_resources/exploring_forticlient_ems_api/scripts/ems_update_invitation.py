'''
ems_update_invitation.py
Updating invitation using the FortiClient EMS API
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
version_major_minor = "7.4"
installer_name = "7.4.7"
fct_comparable = 7004007
system_profile_name = "SYS_EMS-API"
system_profile_id = 0
vpn_profile_name = "VPN_EMS-API"
vpn_profile_id = 0
idp_name = "ad.labdomain.com"
idp_id = 0

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
invitation_url = f'{api_url_prefix}/invitation/4/update'
system_profiles_get_url = f'{api_url_prefix}/profiles/system/index'
vpn_profiles_get_url = f'{api_url_prefix}/profiles/vpn/index'
idps_url = f'{api_url_prefix}/idps/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get system profiles
response = session.get(url=system_profiles_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for profile in response_decoded['data']['local']:
    if profile['name'] == system_profile_name:
        system_profile_id = {profile["id"]}
        #The id is a set, so we convert it to a list and get the only element from it
        system_profile_id = list(system_profile_id)[0]

#Get VPN profiles
response = session.get(url=vpn_profiles_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for profile in response_decoded['data']['local']:
    if profile['name'] == vpn_profile_name:
        vpn_profile_id = {profile["id"]}
        #The id is a set, so we convert it to a list and get the only element from it
        vpn_profile_id = list(vpn_profile_id)[0]

#Get authentication servers data
response = session.get(url=idps_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

#Get all the necessary information directly from the IDP and create the data for the domain import
for idp in response_decoded['data']:
    if idp['domain_info']['name'] == idp_name:
        idp_id = idp['domain_info']['guid']

updated_invitation_data = {
    "name":"API-INVITATION-INSTALLER",
    "comments":"Invitation updated via API",
    "has_email_notifications":False,
    "email_recipients":[],
    "code":"_VjE6MTkyLjE2OC4xLjIwODo4MDEzOmRlZmF1bHQ6NjViNjkwOWItZmI1Mi00ZWEyLTkxMjQtYmVmY2I0ZWFiZGE0",
    "expiry_date":None, #None for no expiry
    "authentication_type":0, #0=None, 1=Local, 2=Domain, 3=SAML
    "email_template_id":1, #?
    "is_bulk":True,
    "listen_address":f"{ems_server}:8013",
    "user_id":None,
    "saml_config_id":None
}

#Update invitation
session.patch(url=invitation_url, json=updated_invitation_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
