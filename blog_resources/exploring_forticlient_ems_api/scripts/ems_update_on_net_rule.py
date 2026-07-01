'''
ems_update_on_net_rule.py
Update on-net rule using the FortiClient EMS API

This updates the on-fabric rule with a new DNS server and public IP
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
on_net_rule_name = "ON-NET_API"

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
on_net_get_url = f'{api_url_prefix}/on_net_rules/index'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

updated_on_net_data = {
    "name":f"{on_net_rule_name}",
    "enabled": True,
    "comments":"On-net rule create via the API",
    "local_ip":"192.0.2.0/24",
    "dns_server_ip":"198.51.100.100",
    "public_ip":"203.0.113.100"
}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get on-net rules information
response = session.get(url=on_net_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

#Get ID of on-net rule, set URL accordingly and update rule
for rule in response_decoded['data']['rule_sets']:
    if rule['name'] == on_net_rule_name:
        on_net_update_url = f'{api_url_prefix}/on_net_rules/{rule['id']}/update'
        session.patch(url=on_net_update_url, json=updated_on_net_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
