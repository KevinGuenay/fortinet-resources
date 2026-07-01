'''
ems_create_installer.py
Create FortiClient installer using the FortiClient EMS API
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

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
installer_url = f'{api_url_prefix}/assignable_installers/create'
system_profiles_get_url = f'{api_url_prefix}/profiles/system/index'
vpn_profiles_get_url = f'{api_url_prefix}/profiles/vpn/index'

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

installer_data = {
    "name":"API-INSTALLER",
    "notes":"FortiClient installer created via API",
    "version_major_minor":version_major_minor,
    "auto_update":None,
    "installer_name":installer_name,
    "fct_comparable":fct_comparable,
    "windows_installer":True,
    "mac_installer":True,
    "linux_installer":True,
    "windows_arm_installer":False,
    "linux_arm_installer":False ,
    "features":[
        5, #Zero Trust Telemetry
        3, #Secure Access Architecture Components
        7, #Vulnerability Scan
        6, #Advanced Persistent Threat (APT) Components
        1, #AntiVirus, Anti-Exploit, Removable Media Access
        10, #Anti-Ransomware
        9, #Cloud Based Malware Outbreak Detection
        2, #Web and Video Filtering
        4, #Application Firewall
        8, #Single Sign-On Mobility Agent
        11, #Zero Trust Network Access
        13, #Privileged Access Agent
        16, #Data Protection
		12#, #FIPS Certification
        #15, #EDR, only in cloud EMS, remove if on-prem EMS
    ],
    "auto_register":True,
    "desktop_shortcut":True,
    "start_menu_shortcut":False,
    "msi_files":True,
    "override_invitation_code":False,
    "group_assignment_rules_id":None,
    "vpn_profile_component_id":vpn_profile_id,
    "system_profile_component_id":system_profile_id,
    "invalid_cert_action":None,
    "telemetry_server_list_id":None
}

#Create installer
response = session.post(url=installer_url, json=installer_data, headers=change_headers, verify=False, timeout=30)
response_decoded = response.content.decode('utf-8')
print(response_decoded)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
