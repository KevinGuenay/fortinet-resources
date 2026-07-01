'''
ems_update_ztna_tag_rule.py
Update a ZTNA tag and associated rule using the FortiClient EMS API

This updates the first rule to target VPN_USERS (from ZTNA_USERS) and the second rule to search for file2.txt (from file1.txt)
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
ztna_tag_name = 'ZTNA-TAG_API'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
ztna_get_url = f'{api_url_prefix}/tags/zero_trust/index'
ztna_update_url = f'{api_url_prefix}/tags/zero_trust/update_one'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#fct_based means the rule is evaluated on FortiClient directly, not on EMS
#The id value in the rules key must be incremented for each rule of a tag
#The type should be the position of the option in the GUI, meaning that the first element of the dropdown is 1, the second 2, etc.
#Not all types where checked if this rule of numbering holds true and this can change in the future
#The os number is in the order in the GUI from left to right, starting at 1 for Windows
#The content is completely dependent on the type of rule used, but most often corresponds to whatever you would enter in a field or what you can select
updated_ztna_data = {
                "name":"ZTNA-TAG_API",
                "description":"This is the User Notification Message",
                "status": True,
                "comments":"Created using the API",
                "rules":[
                    {
                        "negative": False,
                        "content":"GROUPS/VPN_USERS",
                        "domainName":"ad.labdomain.com",
                        "type":1,
                        "os":1,
                        "id":1,
                        "fct_based":True
                    },
                    {
                        "negative": False,
                        "content":"C:\\temp\\file2.txt",
                        "context":"",
                        "type":4,
                        "os":1,
                        "id":2,
                    }
                ],
                "use_custom_logic": False
            }

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Get ZTNA tag information
response = session.get(url=ztna_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for ztna_tag in response_decoded['data']['tags']:
    if ztna_tag['name'] == ztna_tag_name:
        updated_ztna_data['id'] = ztna_tag['id']
        session.post(url=ztna_update_url, json=updated_ztna_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
