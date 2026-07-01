'''
ems_set_server_settings.py
Set server data using the FortiClient EMS API
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
server_settings_url = f'{api_url_prefix}/settings/server/set'

#Variables for data and headers
auth_data = {"name": f"{username}", "password": f"{password}"}
api_headers = {"Content-type": "application/json"}

server_data = {
    "chromebooks": {
        "enabled": False,
        "inactivity_timeout": 24,
        "update_interval": 300,
        "is_licensed": True,
        "service_account": "account-1@forticlientwebfilter.iam.gserviceaccount.com",
        "global_enabled": False,
        "listen_port": 8443,
        "ssl_name": "FCTEMSSERIAL.1.cert",
        "ssl_date": "2056-05-26 20:48:33",
        "chromebook_cert_id": 35,
        "acme_auto_renew": False
    },
    "scheduledBackup": {
        "scheduled_backup_enabled": False,
        "scheduled_backup_type": 1,
        "scheduled_backup_interval": 1,
        "scheduled_backup_start_time": "20:00",
        "scheduled_backup_protocol": 2,
        "scheduled_backup_remote_server_ip": None,
        "scheduled_backup_selected_days": [
            "1",
            "4"
        ],
        "scheduled_backup_password": None,
        "scheduled_backup_compress_type": "database",
        "scheduled_backup_path": "/home/ems/exchange",
        "scheduled_backup_server_type": "local",
        "scheduled_backup_remote_user": None,
        "scheduled_backup_remote_user_password": None,
        "scheduled_backup_retention_period": 15
    },
    "reset_deployment_interval": 12,
    "sws_enabled": False,
    "sws_server": None,
    "sws_cert_name": None,
    "sws_cert_date": None,
    "inv_only_reg_enforcement_type": 0,
    "pwd_changed_check_enforced": False,
    "onboarding_enforced": False,
    "user_auth_period": None,
    "fct_repackager_upload_region": "Europe",
    "endpoints": {
        "key": None,
        "keep_alive_interval": 30,
        "offline_timeout": 15,
        "tag_timeout": 1440,
        "delete_timeout": 30,
        "license_timeout": 0,
        "duplicate_onboarded_user_timeout": 7,
        "unauthed_user_timeout": 30,
        "password_lockout_attempt": 3,
        "password_lockout_period": 60,
        "ztna_token_support": True,
        "ztna_token_timeout": 1440,
        "avatar_upload_enabled": False,
        "snapshot_interval": None
    },
    "unauthed_fct_count": 1,
    "unsupported_fct_count": 0,
    "telemetry": {
        "show_fortigate_server_list": False
    },
    "ztna_cert_date_created": "2026-06-19T08:11:54.217",
    "ztna_cert_expiry_date": "2051-06-13T08:11:54.217",
    "ztna_cert_name": "default_ZTNARootCA.pem",
    "is_custom_ztna_cert": False,
    "custom_hostname": "",
    "public_address": "ems.ad.labdomain.com",
    "public_port": 443,
    "https_enabled": True,
    "https_redirect_enabled": True,
    "ssl_from_forti_care": False,
    "custom_ec_cert": True,
    "enable_persistent_connection": True,
    "installer_port_enabled": True,
    "fos_notify_server_port": 8015,
    "webserver_cert_id": 36,
    "ec_cert_id": 36,
    "auto_upgrade_enabled": True,
    "hostname": "EMS",
    "is_ip_invalid": False,
    "listen_port": 8013,
    "fqdn_enabled": True,
    "fqdn": "ems.ad.labdomain.com",
    "installer_ip": "fcems-server",
    "show_fortigate_server_list": False,
    "password_lockout_attempt": 3,
    "password_lockout_period": 60,
    "ha_alert_interval": 60,
    "acme_auto_renew": False,
    "predefined_hostname": "*,192.168.1.208",
    "https_port": 443,
    "sites_enabled": False,
    "is_fgt_connected": False,
    "login_banner": {
        "enabled": False,
        "message": ""
    },
    "ips": [
        "192.168.1.208"
    ],
    "listen_ip": "0.0.0.0",
    "installer_port": 10443
}

#Setup session, login to EMS, and set new headers with CSRF token and referer
session = requests.Session()
login_response = session.post(url=login_url, json=auth_data, headers=api_headers, verify=False, timeout=30)
change_headers = {"Content-type": "application/json", "Referer": f"https://{ems_server}", "X-CSRFToken": f"{session.cookies["csrftoken"]}"}

#Set server settings
session.patch(url=server_settings_url, data=server_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
