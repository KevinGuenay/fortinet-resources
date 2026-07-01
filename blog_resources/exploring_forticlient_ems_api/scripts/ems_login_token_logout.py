'''
ems_login_token_logout.py
Perform a login on the FortiClient EMS API, get the CSRF token and then logout
'''

import requests

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Disable warnings
requests.urllib3.disable_warnings()

#Set some variables for the API
ems_server = '192.168.1.208'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
