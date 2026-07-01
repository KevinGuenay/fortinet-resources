'''
ems_create_on_net_rule.py
Create on-net rule using the FortiClient EMS API
'''

import requests

#Disable warnings
requests.urllib3.disable_warnings()

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Set some variables for the API
ems_server = '192.168.1.208'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
on_net_url = f'{api_url_prefix}/on_net_rules/create'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}
on_net_data = {
    "name":"ON-NET_API",
    "enabled": True,
    "comments":"On-net rule created via the API",
    "local_ip":"192.0.2.0/24",
    "dns_server_ip":"198.51.100.1",
    "public_ip":"203.0.113.1"
}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Create on-net rule
session.post(url=on_net_url, json=on_net_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
