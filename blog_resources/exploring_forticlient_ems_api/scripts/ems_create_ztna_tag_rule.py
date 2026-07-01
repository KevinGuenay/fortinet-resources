'''
ems_create_ztna_tag_rule.py
Create a ZTNA tag and associated rule using the FortiClient EMS API
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
ztna_url = f'{api_url_prefix}/tags/zero_trust/create'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

#fct_based means the rule is evaluated on FortiClient directly, not on EMS
#The id value in the rules key must be incremented for each rule of a tag
#The type should be the position of the option in the GUI, meaning that the first element of the dropdown is 1, the second 2, etc.
#Not all types where checked if this rule of numbering holds true and this can change in the future
#The os number is in the order in the GUI from left to right, starting at 1 for Windows
#The content is completely dependent on the type of rule used, but most often corresponds to whatever you would enter in a field or what you can select
ztna_data = {
                "name":"ZTNA-TAG_API",
                "description":"This is the User Notification Message",
                "status": True,
                "comments":"Created using the API",
                "rules":[
                    {
                        "negative": False,
                        "content":"GROUPS/ZTNA_USERS",
                        "domainName":"ad.labdomain.com",
                        "type":1,
                        "os":1,
                        "id":1,
                        "fct_based":True
                    },
                    {
                        "negative": False,
                        "content":"C:\\temp\\file1.txt",
                        "context":"",
                        "type":4,
                        "os":1,
                        "id":2,
                    }
                ],
                "use_custom_logic": False
            }

ztna_data_custom_logic = {
                "name":"ZTNA-TAG-CUSTOM-LOGIC_API",
                "description":"This is the User Notification Message",
                "status": True,
                "comments":"Created using the API with custom logic",
                "rules":[
                    {
                        "negative": False,
                        "content":"GROUPS/ZTNA_USERS",
                        "domainName":"ad.labdomain.com",
                        "type":1,
                        "os":1,
                        "id":1,
                        "fct_based":True
                    },
                    {
                        "negative": False,
                        "content":"C:\\temp\\file1.txt",
                        "context":"",
                        "type":4,
                        "os":1,
                        "id":2,
                    }
                ],
                "use_custom_logic": True,
                    "logic":{
                        "android": None,
                        "ios": None,
                        "linux": None,
                        "mac": None,
                        "windows":"{\"op\":\"or\",\"rules\":[{\"id\":1},{\"id\":2}]}"
                    }
            }

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Create ZTNA tag and rule
session.post(url=ztna_url, json=ztna_data, headers=change_headers, verify=False, timeout=30)

#Create ZTNA tag and rule with custom logic
session.post(url=ztna_url, json=ztna_data_custom_logic, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
