'''
ems_import_set_certificate_pkcs12.py
Import a certificate in PKCS#12 format and set it as the server certificate, endpoint certificate, and Chromebook certificate in FortiClient EMS.
'''

import os
import json
import requests

def form_value(v):
    '''
    Function author: Claude Opus 5.5
    Return correctly formatted value for multipart/form-data request
    '''
    if isinstance(v, bool):
        return "true" if v else "false" #Browser sends lowercase, Python's str() gives "True"
    if isinstance(v, list):
        return json.dumps(v) #Browser sends the list as the string ["1","4"]
    return str(v)

#Disable warnings
requests.urllib3.disable_warnings()

#Set credentials
username = 'apiadmin'
password = 'Start123$'

#Set some variables for the API
ems_server = '192.168.1.177'
pfx_path = "E:\\temp\\ems.ad.labdomain.com.pfx"
pfx_password = 'ems'

#Set all used URLs
api_url_prefix = f'https://{ems_server}/api/v1'
login_url = f'{api_url_prefix}/auth/signin'
logout_url = f'{api_url_prefix}/auth/signout'
pkcs12_url = f'{api_url_prefix}/server_certificates/upload_pkcs12'
server_url = f'{api_url_prefix}/settings/server/set'

#Variables for data and headers
auth_data = f'{{"name": "{username}", "password": "{password}"}}'
api_headers = '{"Content-type": "application/json"}'

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=json.loads(auth_data), headers=json.loads(api_headers), verify=False, timeout=30)

#When doing form-based/multipart requests we should not set a Content-type header.
multipart_headers = f'{{"Referer": "https://{ems_server}", "X-CSRFToken": "{session.cookies["csrftoken"]}"}}'
change_headers = f'{{"Content-type": "application/json", "Referer": "https://{ems_server}", "X-CSRFToken": "{session.cookies["csrftoken"]}"}}'

with open(pfx_path, "rb") as pfx:
    response = session.post(url=pkcs12_url, files={"cert": (os.path.basename(pfx_path), pfx, "application/x-pkcs12")}, data={"password": pfx_password}, headers=json.loads(multipart_headers), verify=False, timeout=30)

response_decoded = response.content.decode('utf-8')

if response.status_code == 400:
    print(f"ERROR uploading certificate: {response_decoded}")
elif response.status_code == 200:
    cert_id = json.loads(response_decoded)['data']['id']

    #A dictionary containing various values for EMS settings. Only some are actually used, but for documentation purposes several are included here.
    #Comments are included to show why some valures are set.
    #Values valid as of FortiClient EMS 7.4.8
    ems_settings = {
        "hostname": "LAB-EMS", #Required, because without it nothing is actually being done, despite the response being successful.
        # "listen_ip": "0.0.0.0",
        # "fqdn_enabled": True,
        # "fqdn": "ems.ad.labdomain.com",
        # "https_enabled": True,
        # "custom_hostname": "ems-installer.ad.labdomain.com",
        # "public_address": "ems.ad.labdomain.com",
        # "public_port": 443,
        # "https_redirect_enabled": True,
        # "password_lockout_attempt": 3,
        # "password_lockout_period": 60,
        # "ha_alert_interval": 60,
        "webserver_cert_id": f"{cert_id}",
        "ec_cert_id": f"{cert_id}",
        "custom_ec_cert": True,
        # "stats_enabled": True,
        # "reset_deployment_interval": 12,
        # "ztna_token_timeout": 1440,
        # "ztna_token_support": False,
        # "listen_port": 8013,
        # "installer_ip": "ems-installer.ad.labdomain.com",
        # "installer_port_enabled": True,
        "installer_port": 10443, #Required, because otherwise you get an error that it is missing.
        # "enable_persistent_connection": True,
        # "fos_notify_server_port": 8015,
        "login_banner_enabled": False, #Optional, but is set because otherwise you get an error with a weird message, though the correct settings are applied.
        # "login_banner_message": "",
        # "auto_upgrade_enabled": True,
        # "onboarding_enforced": False,
        # "user_auth_period": 0,
        # "endpoints_user_device_reg_limit": 0,
        # "pwd_changed_check_enforced": False,
        # "sws_enabled": False,
        # "fct_repackager_upload_region": "Europe",
        # "inv_only_reg_enforcement_type": 0,
        # "ems_local_subnets_only": False,
        "chromebooks_enabled": True, #Required for Chromebook functionality, because otherwise you get an error that it is missing.
        "chromebooks_inactivity_timeout": 24, #Required for Chromebook functionality, because otherwise you get an error that it is missing.
        "chromebooks_update_interval": 300, #Required for Chromebook functionality, because otherwise you get an error that it is missing.
        "chromebooks_global_enabled": True, #Required for Chromebook functionality, because otherwise you get an error that it is missing.
        "chromebooks_listen_port": 8443, #Required for Chromebook functionality, because otherwise you get an error that it is missing.
        "chromebook_cert_id": f"{cert_id}",
        # "scheduled_backup_enabled": False,
        # "scheduled_backup_type": 1,
        # "scheduled_backup_interval": 1,
        # "scheduled_backup_start_time": "20:00",
        # "scheduled_backup_protocol": 2,
        # "scheduled_backup_selected_days": ["1", "4"],
        # "scheduled_backup_password": "",
        # "scheduled_backup_server_type": "local",
        # "scheduled_backup_compress_type": "database",
        # "scheduled_backup_path": "/home/ems/exchange",
        # "scheduled_backup_retention_period": 15,
        # "endpoints_key": "",
        # "endpoints_keep_alive_interval": 20,
        # "endpoints_offline_timeout": 30,
        # "endpoints_tag_timeout": 1,
        # "endpoints_delete_timeout": 30,
        # "endpoints_license_timeout": 0,
        # "endpoints_duplicate_onboarded_user_timeout": 7,
        # "endpoints_password_lockout_attempt": 3,
        # "endpoints_password_lockout_period": 60,
        # "endpoints_unauthed_user_timeout": 30,
        # "endpoints_avatar_upload_enabled": False,
        # "endpoints_token_timeout": 15,
        # "sites_enabled": False
    }

    #EMS wants the data in a multipart/form-data format for the server settings, so we need to convert the dictionary into that format.
    multipart = {k: (None, form_value(v)) for k, v in ems_settings.items()}

    #Set the server certificate
    response = session.patch(url=server_url, files=multipart, headers=json.loads(multipart_headers), verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=json.loads(change_headers), verify=False, timeout=30)
