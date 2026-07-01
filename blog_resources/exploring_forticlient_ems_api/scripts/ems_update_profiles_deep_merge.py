'''
ems_update_profiles_deep_merge.py
Update a system and a remote access VPN profile by first importing the existing configuration using the FortiClient EMS API

This script updates the system settings profile created in ems_create_profiles.py by disabling security posting tags on the GUI and disabling bubble notifications
This script updates the VPN profile created in ems_create_profiles.py by
* Enabling the save username option
* Changing the remote gateway
* Changing the phase 1 DH group
* Enabling session resume
* Changing the phase 2 proposals
* Disabling personal VPNs
'''

import json
import requests

#Disable warnings
requests.urllib3.disable_warnings()

def deep_merge(base, override):
    """
    Function written by Claude Sonnet 4.6

    Recursively merge `override` into `base`.
    - Dicts: merged recursively.
    - Lists of dicts with a 'name' key: matched by name, then merged recursively.
    - Everything else: override replaces base.
    """
    if isinstance(base, dict) and isinstance(override, dict):
        result = base.copy()
        for key, override_val in override.items():
            base_val = result.get(key)
            result[key] = deep_merge(base_val, override_val)
        return result

    if (
        isinstance(base, list)
        and isinstance(override, list)
        and all(isinstance(i, dict) and "name" in i for i in base + override)
    ):
        # Match connection objects by 'name', merge matched pairs
        base_by_name = {item["name"]: item for item in base}
        result = []
        for override_item in override:
            name = override_item["name"]
            if name in base_by_name:
                result.append(deep_merge(base_by_name[name], override_item))
            else:
                result.append(override_item)  # new entry, add as-is
        # Preserve base entries not present in override
        override_names = {item["name"] for item in override}
        for base_item in base:
            if base_item["name"] not in override_names:
                result.append(base_item)
        return result

    # Scalar, plain list, or mismatched types: override wins
    return override

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Set some variables for the API
ems_server = '192.168.1.208'
temp_password = 'Start123$'
system_profile_name = "SYS_EMS-API"
vpn_profile_name = "VPN_EMS-API"
vpn_ipsec_connection_name = "API-IPSEC-VPN"

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
system_profiles_get_url = f'{api_url_prefix}/profiles/system/index'
vpn_profiles_get_url = f'{api_url_prefix}/profiles/vpn/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

updated_system_profile_data = {
    "json": {
        "system": {
            "ui": {
                "show_host_tag": 0,
            }
        },
        "endpoint_control": {
            "show_bubble_notifications": 0,
        }
    }
}

updated_vpn_profile_data = {
    "name": f"{vpn_profile_name}",
    "json": {
        "vpn": {
            "ipsecvpn": {
                "connections": [
                    {
                        "name": f"{vpn_ipsec_connection_name}",
                        "ui": {
                            "save_username": 1
                        },
                        "ike_settings": {
                            "server": "192.0.2.254",
                            "dhgroup": [21],
                            "session_resume": 1,
                        },
                        "ipsec_settings": {
                            "proposals": [
                                {
                                    "encryption": "AES256GCM",
                                    "authentication": "NONE"
                                },
                                {
                                    "encryption": "AES256",
                                    "authentication": "SHA512"
                                }
                            ]
                        },
                    }
                ]
            },
            "options": {
                "allow_personal_vpns": 0,
            }
        }
    }
}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get system profiles
response = session.get(url=system_profiles_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for profile in response_decoded['data']['local']:
    if profile['name'] == system_profile_name:
        system_profile_get_url = f'{api_url_prefix}/profiles/system/{profile["id"]}/get'
        response = session.get(url=system_profile_get_url, headers=api_headers, verify=False, timeout=30)
        response_decoded = json.loads(response.content.decode('utf-8'))
        system_profile_data = response_decoded['data']

        #Update system_profile_data with the updated information
        system_profile_data = deep_merge(system_profile_data, updated_system_profile_data)

        #Set the correct URL for updating the system profile using the profile ID
        system_profile_update_url = f'{api_url_prefix}/profiles/system/{profile["id"]}/update'
        #Update system profile
        session.put(url=system_profile_update_url, json=system_profile_data, headers=change_headers, verify=False, timeout=30)

#Get VPN profiles
response = session.get(url=vpn_profiles_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for profile in response_decoded['data']['local']:
    if profile['name'] == vpn_profile_name:
        vpn_profile_get_url = f'{api_url_prefix}/profiles/vpn/{profile["id"]}/get'
        response = session.get(url=vpn_profile_get_url, headers=api_headers, verify=False, timeout=30)
        response_decoded = json.loads(response.content.decode('utf-8'))
        vpn_profile_data = response_decoded['data']

        #Update vpn_profile_data with the updated information
        #update_dictionary(vpn_profile_data['json']['vpn'], updated_vpn_profile_data['json']['vpn'])
        vpn_profile_data = deep_merge(vpn_profile_data, updated_vpn_profile_data)

        #Set the correct URL for updating the VPN profile using the profile ID
        vpn_profile_update_url = f'{api_url_prefix}/profiles/vpn/{profile["id"]}/update'
        #Update VPN profile
        session.put(url=vpn_profile_update_url, json=vpn_profile_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
