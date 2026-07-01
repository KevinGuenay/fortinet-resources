'''
ems_update_policy.py
Update a policy with profiles for AD OUs and groups and an on-net rule using the FortiClient EMS API
This script updates the policy by setting different groups (from VPN_USERS to ZTNA_USERS) and a different VPN profile in the off-net profile components (from VPN_EMS-API to Default)
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
policy_name = "POLICY_API"

#Adding groups and OUs to a policy is a bit complicated, so here is an example.
#Consider the following AD structure:

#ad.labdomain.com
#└── CLIENTS
#└── GROUPS
#   ├── VPN_USERS
#   ├── ZTNA_USERS
#└── SERVERS
#   └── PROD

#If you want to assign the entire CLIENTS OU to a policy add the name to the assigned_ous list
#The script will get the ID of the OU and add it to the list of IDs that should get added to the policy

#If you want to add the VPN_USERS group to a policy and using the structure from above you first have to get the GUID of the GROUPS OU
#With the GUID you can then look up all the groups in that OU and get the ID for the group and add that to the list of IDs that should get added to the policy
#In order to facilitate this add the parent OU to the parent_ous list and the groups you want to assign, that are in the parent OU, to the assigned_group_names list

assigned_ous = ["CLIENTS"]
parent_ous = ['GROUPS', 'SERVERS']
assigned_group_names = ['PROD', 'ZTNA_USERS']

on_net_rule_name = "ON-NET_API"
ou_group_ids = []
on_net_rule_id = 0

#You just need to supply the name for the desired profile
on_net_profiles = {
        "vpn": {'name':'Default'},
        "ztna": {'name':'Default'},
        "webfilter": {'name':'Default'},
        "videofilter": {'name':'Default'},
        "vulnerability_scan": {'name':'Default'},
        "malware": {'name':'Default'},
        "sandbox": {'name':'Default'},
        "firewall": {'name':'Default'},
        "ftdata_scan": {'name':'Default'},
        "system": {'name':'SYS_EMS-API'}
}
off_net_profiles = {
        "vpn": {'name':'Default'},
        "ztna": {'name':'Default'},
        "webfilter": {'name':'Default'},
        "videofilter": {'name':'Default'},
        "vulnerability_scan": {'name':'Default'},
        "malware": {'name':'Default'},
        "sandbox": {'name':'Default'},
        "firewall": {'name':'Default'},
        "ftdata_scan": {'name':'Default'},
        "system": {'name':'SYS_EMS-API'}
}

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
policy_get_url = f'{api_url_prefix}/endpoint_policies/index'
idps_url = f'{api_url_prefix}/idps/index'
on_net_url = f'{api_url_prefix}/on_net_rules/index'

#This list is used later to loop through so we don't need to reuse code
profile_type_names = ['vpn', 'ztna','webfilter','videofilter','vulnerability_scan','malware','sandbox','firewall','ftdata_scan','system']

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

#Get imported OUs from IDPS and add the IDs to the ou_group_ids list
for idp in response_decoded['data']:
    if idp['domain_info']['name'] == idp_name:
        idp_id = idp['domain_info']['guid']
        idp_groups_url = f'{api_url_prefix}/idps/adfs/{idp_id}/imported_ous'
        response = session.get(url=idp_groups_url, headers=api_headers, verify=False, timeout=30)
        response_decoded = json.loads(response.content.decode('utf-8'))

        #The two ifs are used to search for the OU name in the assigned OUs, if we want to assign an entire OU to a policy and search through the parent OUs if we need to assign groups in OUs
        for ou in response_decoded['data']['group_containers']:
            if ou['name'] in assigned_ous or ou['name'] in assigned_group_names:
                ou_group_ids.append(ou['id'])
            if ou['name'] in parent_ous:
                ou_groups_url = f'{api_url_prefix}/idps/adfs/{ou['guid']}/imported_ous'
                response = session.get(url=ou_groups_url, headers=api_headers, verify=False, timeout=30)
                response_decoded = json.loads(response.content.decode('utf-8'))
                for group in response_decoded['data']['group_containers']:
                    if group['name'] in assigned_group_names:
                        ou_group_ids.append(group['id'])

#We create a list that will hold dictionaries with each ID that should be assigned to the policy
endpoint_group_ids = []

for id_entry in ou_group_ids:
    id_dict = {"id":id_entry}
    endpoint_group_ids.append(id_dict)

#Get on-net rules and set ID based on given name
response = session.get(url=on_net_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for rule in response_decoded['data']['rule_sets']:
    if rule['name'] == on_net_rule_name:
        on_net_rule_id = rule['id']

#Loop through all profile types and add the ID for each named profile to the dictionary
for profile_type in profile_type_names:
    profile_url = f'{api_url_prefix}/profiles/{profile_type}/index'
    response = session.get(url=profile_url, headers=api_headers, verify=False, timeout=30)
    response_decoded = json.loads(response.content.decode('utf-8'))

    for profile in response_decoded['data']['local']:
        if profile['name'] == on_net_profiles[f'{profile_type}']['name']:
            on_net_profiles[f'{profile_type}']['id'] = profile['id']
        if profile['name'] == off_net_profiles[f'{profile_type}']['name']:
            off_net_profiles[f'{profile_type}']['id'] = profile['id']

updated_policy_data = {
    "name":"POLICY_API",
    "endpoint_groups":endpoint_group_ids,
    "enable_on_off_net":True,
    "profile_components":{
        "vpn":{
            "id":on_net_profiles['vpn']['id'],
        },
        "ztna":{
            "id":on_net_profiles['ztna']['id'],
        },
        "webfilter":{
            "id":on_net_profiles['webfilter']['id'],
        },
        "videofilter":{
            "id":on_net_profiles['videofilter']['id'],
        },
        "vulnerability_scan":{
            "id":on_net_profiles['vulnerability_scan']['id'],
        },
        "malware":{
            "id":on_net_profiles['malware']['id'],
        },
        "sandbox":{
            "id":on_net_profiles['sandbox']['id'],
        },
        "firewall":{
            "id":on_net_profiles['firewall']['id'],
        },
        "ftdata_scan":{
            "id":on_net_profiles['ftdata_scan']['id'],
        },
        "system":{
            "id":on_net_profiles['system']['id'],
        }
    },
    "off_net_profile_components":{
        "vpn":{
            "id":off_net_profiles['vpn']['id'],
        },
        "ztna":{
            "id":off_net_profiles['ztna']['id'],
        },
        "webfilter":{
            "id":off_net_profiles['webfilter']['id'],
        },
        "videofilter":{
            "id":off_net_profiles['videofilter']['id'],
        },
        "vulnerability_scan":{
            "id":off_net_profiles['vulnerability_scan']['id'],
        },
        "malware":{
            "id":off_net_profiles['malware']['id'],
        },
        "sandbox":{
            "id":off_net_profiles['sandbox']['id'],
        },
        "firewall":{
            "id":off_net_profiles['firewall']['id'],
        },
        "ftdata_scan":{
            "id":off_net_profiles['ftdata_scan']['id'],
        },
        "system":{
            "id":off_net_profiles['system']['id'],
        }
    },
    "telemetry_server_list":None,
    "on_net_rules":[
        {
            "id":on_net_rule_id,
        }
    ],
    "comments":"Test",
    "enabled":True,
}

#Get policy ID, set patch URL and update policy
response = session.get(url=policy_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for policy in response_decoded['data']:
    if policy['name'] == policy_name:
        policy_update_url = f'{api_url_prefix}/endpoint_policies/{policy['id']}/update'

        #Update policy
        session.patch(url=policy_update_url, json=updated_policy_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
