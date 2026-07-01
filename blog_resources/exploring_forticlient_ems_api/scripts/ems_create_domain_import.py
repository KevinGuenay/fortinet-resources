'''
ems_create_domain_import.py
Create a domain import using the FortiClient EMS API
'''

import urllib.parse
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

#Adding groups and OUs to a policy is a bit complicated, so here is an example.
#Consider the following AD structure:

#ad.labdomain.com
#└── CLIENTS
#└── GROUPS
#   ├── VPN_USERS
#   ├── ZTNA_USERS
#└── SERVERS
#   └── PROD

#If you want to import the entire CLIENTS OU add the name to the assigned_ous list
#The script will get the required information of the OU and create a dictionary for the import

#If you want to import the VPN_USERS group, and using the structure from above, you first have add the parent OU to the parent_ous list
#In the example the parent OU is GROUP
#Then add the VPN_USERS group to the assigned_group_names list

assigned_ous = ['CLIENTS','SERVERS']
parent_ous = ['GROUPS']
assigned_group_names = ['VPN_USERS','ZTNA_USERS']
assigned_ous_groups = []

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

#Get all the necessary information directly from the IDP and create the data for the domain import
for idp in response_decoded['data']:
    if idp['domain_info']['name'] == idp_name:
        idp_id = idp['domain_info']['guid']
        #The DN has to be URL encoded
        idp_dn_urlencoded = urllib.parse.quote(idp['connection_info']['basedn'], safe="")
        domain_import_url = f'{api_url_prefix}/idps/adfs/{idp_id}/patch'
        #The live navigation is used to get the information regarding the directory structure straight from the authentication server
        live_navigation_url = f'{api_url_prefix}/idps/{idp_id}/live_navigate?dn={idp_dn_urlencoded}'

        #The response from the live navigation contains the directory structure with all OUs, but not groups
        response = session.get(url=live_navigation_url, headers=api_headers, verify=False, timeout=30)
        response_decoded = json.loads(response.content.decode('utf-8'))

        #The two ifs are used to search for the OU name in the assigned OUs, if we want to import an entire OU, and search through the parent OUs if we need to import groups in OUs
        for ou in response_decoded['data']:
            if ou['name'] in assigned_ous:
                #A temporary dictionary is used to store the information for the to-be-imported object
                temp_dict = {"guid": ou['guid'], "name": ou['name'], "dn": ou['dn'], "path": ou['canonical_name'], }
                #The temporary dictionary gets added to a list
                assigned_ous_groups.append(temp_dict)
            #Much the same is done for groups, except we first have to go through the OUs, like with the initial authentication server
            if ou['name'] in parent_ous:
                ou_dn_urlencoded = urllib.parse.quote(ou['dn'], safe="")
                groups_live_navigation_url = f'{api_url_prefix}/idps/{idp_id}/live_navigate?dn={ou_dn_urlencoded}'
                response = session.get(url=groups_live_navigation_url, headers=api_headers, verify=False, timeout=30)
                response_decoded = json.loads(response.content.decode('utf-8'))
                for group in response_decoded['data']:
                    if group['name'] in assigned_group_names:
                        temp_dict = {"guid": group['guid'], "name": group['name'], "dn": group['dn'], "path": group['canonical_name'], }
                        assigned_ous_groups.append(temp_dict)

        #With all the dictionaries in the list we can assemble the JSON payload
        domain_data = {
            "sync_mins":60,
            "is_imported": True,
            "selected_group_containers": assigned_ous_groups
        }

        #Create domain import
        session.patch(url=domain_import_url, json=domain_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
