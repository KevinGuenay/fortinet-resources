'''
ems_update_profiles_entire_data.py
Update a system and a remote access VPN profile using the FortiClient EMS API by supplying the entire data instead of performing a copy

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

#Supply the entire JSON for the profile. If you only provide parts defaults will be used for the missing settings.
system_profile_data = {
    "name": f"{system_profile_name}",
    "is_chromebook": False,
    "enabled": True,
    "display_enabled": True,
    "clone_from": None,
    "json": {
        "system": {
            "ui": {
                "disable_backup": 0,
                "hide_user_info": 0,
                "hide_system_tray_icon": 0,
                "show_host_tag": 1,
                "password": f"{temp_password}",
                "lock": f"{temp_password}",
                "unreg_pwd": f"{temp_password}",
                "culture_code": "os-default",
                "default_tab": "VPN",
                "allow_shutdown_when_registered": 0
            },
            "log_settings": {
                "onnet_local_logging": 1,
                "level": 6,
                "log_events": "antiexploit,antiransomware,av,cloudscan,endpoint,firewall,fssoma,ipsecvpn,pam,sandboxing,sslvpn,update,vuln,webfilter,ztna,configd,scheduler,shield,wanacc",
                "remote_logging": {
                    "log_upload_enabled": 0,
                    "log_retention_days": 90,
                    "log_upload_freq_minutes": 60,
                    "send_software_inventory": 0,
                    "send_os_events": {
                        "enabled": 1,
                        "interval": 120
                    },
                    "log_upload_server": "",
                    "log_upload_ssl_enabled": 1,
                    "log_generation_timeout_secs": 900,
                    "log_compressed": 0,
                    "netlog_categories": 32
                }
            },
            "proc_protect": 1,
            "proxy": {
                "update": 0,
                "fail_over_to_fdn": 0,
                "online_scep": 0,
                "virus_submission": 0,
                "type": "http",
                "address": None,
                "port": "80",
                "username": None,
                "password": ""
            },
            "update": {
                "use_custom_server": 0,
                "timeout": 60,
                "failoverport": 8000,
                "auto_patch": 0,
                "update_action": "disable",
                "scheduled_update": {
                    "enabled": 1,
                    "type": "interval",
                    "daily_at": "00:00",
                    "update_interval_in_hours": 1
                },
                "submit_virus_info_to_fds": 1,
                "submit_vuln_info_to_fds": 1,
                "use_legacy_fdn": 0,
                "server": "",
                "port": 80,
                "fail_over_to_fdn": 0,
                "restrict_services_to_regions": "",
                "ocsp_mode": 0
            },
            "fortiproxy": {
                "enabled": 1,
                "enable_https_proxy": 1,
                "http_timeout": 60,
                "client_comforting": {
                    "pop3_client": 1,
                    "pop3_server": 1,
                    "smtp": 1
                },
                "selftest": {
                    "enabled": 1,
                    "last_port": 65535,
                    "notify": 1
                }
            },
            "certificates": [31],
            "user_identity": {
                "enable_manually_entering": 0,
                "enable_linkedin": 0,
                "enable_google": 0,
                "enable_salesforce": 0,
                "notify_user": 0
            },
            "installer": {
                "allow_admin_uninstall_when_locked": 1
            },
            "cryptography": {
                "drbg_reseed_minutes": 1440
            }
        },
        "extra": {
            "trigger_vuln_scan": True
        },
        "endpoint_control": {
            "ui": {
                "hide_compliance_warning": 0
            },
            "notify_fgt_on_logoff": 0,
            "forensics_license": 1,
            "enable_dem": 0,
            "disable_unregister": 1,
            "disable_fgt_switch": 0,
            "show_bubble_notifications": 1,
            "send_software_inventory": 0,
            "invalid_cert_action": "warn",
            "edr_collector": 1,
            "enable_dns_cache": 0,
            "auto_start": 0
        },
        "fssoma": {
            "enabled": 0,
            "serveraddress": "",
            "presharedkey": ""
        },
        "wan_optimization": {
            "enabled": 0,
            "max_disk_cache_size_mb": 512,
            "support_http": 1,
            "support_cifs": 1,
            "support_mapi": 1,
            "support_ftp": 1
        },
        "pam": {
            "enabled": 0,
            "default_port": 9191
        }
    }
}

#Supply the entire JSON for the profile. If you only provide parts defaults will be used for the missing settings.
vpn_profile_data = {
    "name": f"{vpn_profile_name}",
    "is_chromebook": False,
    "enabled": True,
    "display_enabled": True,
    "clone_from": None,
    "json": {
        "vpn": {
            "display_vpn": 1,
            "enabled": 1,
            "sslvpn": {
                "options": {
                    "enabled": 0,
                    "prefer_sslvpn_dns": 1,
                    "disallow_invalid_server_certificate": 0,
                    "warn_invalid_server_certificate": 1,
                    "preferred_dtls_tunnel": 0,
                    "show_auth_cert_only": 0,
                    "use_gui_saml_auth": 0,
                    "block_ipv6": 1,
                    "dnscache_service_control": 0,
                    "no_dns_registration": 0,
                    "negative_split_tunnel_metric": None,
                    "mtu_size": 1300,
                    "dtls_mtu": 1100
                },
                "connections": []
            },
            "ipsecvpn": {
                "options": {
                    "enabled": 1,
                    "use_win_current_user_cert": 1,
                    "use_win_local_computer_cert": 1,
                    "beep_if_error": 0,
                    "usewincert": 1,
                    "usesmcardcert": 1,
                    "use_gui_saml_auth": 0,
                    "block_ipv6": 1,
                    "enable_udp_checksum": 0,
                    "disable_default_route": 0,
                    "show_auth_cert_only": 0,
                    "check_for_cert_private_key": 0,
                    "enhanced_key_usage_mandatory": 0,
                    "disallow_invalid_server_certificate": 0,
                    "prefer_ipsecvpn_dns": 1,
                    "no_dns_registration": 0,
                    "mtu_size": 1280
                },
                "connections": [
                    {
                        "name": f"{vpn_ipsec_connection_name}",
                        "pinned": 0,
                        "dns_priority": 1,
                        "machine": None,
                        "keep_running": 0,
                        "traffic_keep_strategy": 0,
                        "traffic_keep_timer": 5000,
                        "disclaimer_msg": "",
                        "single_user_mode": 0,
                        "ui": {
                            "show_remember_password": 0,
                            "show_alwaysup": 0,
                            "show_autoconnect": 0,
                            "show_passcode": 0,
                            "save_username": 0
                        },
                        "traffic_control": {
                            "enabled": 0,
                            "mode": 1,
                            "apps": [],
                            "fqdns": [],
                            "isdb_objects": [],
                            "vsdb_objects": []
                        },
                        "redundant_sort_method": 0,
                        "tags": {
                            "allowed": "",
                            "prohibited": ""
                        },
                        "host_check_fail_warning": "",
                        "ike_settings": {
                            "server": "192.0.2.1",
                            "authentication_method": "Preshared Key",
                            "auth_data": f"{temp_password}",
                            "transport_mode": 0,
                            "tcp_port": 443,
                            "udp_port": 500,
                            "cert_subjectcheck": 0,
                            "prompt_certificate": 1,
                            "xauth_timeout": 120,
                            "xauth": {
                                "use_otp": 0,
                                "enabled": 0,
                                "prompt_username": 0
                            },
                            "version": 2,
                            "mode": "aggressive",
                            "dhgroup": [31],
                            "key_life": 28800,
                            "localid": None,
                            "networkid": 0,
                            "eap_method": 1,
                            "implied_SPDO": 0,
                            "implied_SPDO_timeout": 60,
                            "nat_traversal": 1,
                            "enable_local_lan": 1,
                            "session_resume": 0,
                            "enable_ike_fragmentation": 1,
                            "mode_config": 1,
                            "modeconfig_type": 0,
                            "dpd": 1,
                            "proposals": [
                                {
                                    "encryption": "AES128",
                                    "authentication": "SHA256"
                                },
                                {
                                    "encryption": "AES256",
                                    "authentication": "SHA256"
                                }
                            ],
                            "run_fcauth_system": 0,
                            "failover_sslvpn_connection": None,
                            "sso_enabled": 0,
                            "use_external_browser": 0,
                            "ike_saml_port": 443,
                            "keep_fqdn_resolution_consistency": 0,
                            "no_vnic_dns_server": 0,
                            "azure_auto_login": {
                                "enabled": 0,
                                "azure_app": {
                                    "tenant_name": "",
                                    "client_id": ""
                                }
                            }
                        },
                        "ipsec_settings": {
                            "remote_networks": [
                                {
                                    "addr": "0.0.0.0",
                                    "mask": "0.0.0.0"
                                },
                                {
                                    "addr": "::/0",
                                    "mask": "::/0"
                                }
                            ],
                            "dhgroup": 31,
                            "key_life_type": "seconds",
                            "key_life_seconds": 3600,
                            "key_life_Kbytes": 5200,
                            "replay_detection": 1,
                            "pfs": 1,
                            "virtualip": {
                                "type": "modeconfig",
                                "ip": "0.0.0.0",
                                "mask": "0.0.0.0",
                                "dnsserver": "0.0.0.0",
                                "winserver": "0.0.0.0"
                            },
                            "proposals": [
                                {
                                    "encryption": "AES128GCM",
                                    "authentication": "NONE"
                                },
                                {
                                    "encryption": "AES256",
                                    "authentication": "SHA256"
                                }
                            ],
                            "ipv4_split_exclude_networks": []
                        },
                        "on_connect": [
                            {
                                "os": "windows",
                                "script": ""
                            },
                            {
                                "os": "MacOSX",
                                "script": ""
                            }
                        ],
                        "on_disconnect": [
                            {
                                "os": "windows",
                                "script": ""
                            },
                            {
                                "os": "MacOSX",
                                "script": ""
                            }
                        ],
                        "android_cert_path": ""
                    }
                ]
            },
            "lockdown": {
                "enabled": 0,
                "grace_period": 120,
                "max_attempts": 3,
                "exceptions": {
                    "apps": None,
                    "ips": None,
                    "domains": None,
                    "icdb_domains": []
                },
                "detect_captive_portal": {
                    "enabled": 0,
                    "os_active_probing": 1
                }
            },
            "options": {
                "current_connection_name": "",
                "current_connection_type": None,
                "autoconnect_tunnel": "",
                "vendor_id": None,
                "on_os_start_connect": "",
                "on_os_start_connect_has_priority": 0,
                "show_vpn_before_logon": 1,
                "minimize_window_on_connect": 1,
                "use_windows_credentials": 0,
                "suppress_vpn_notification": 0,
                "secure_remote_access": 0,
                "certs_require_keyspec": 0,
                "disable_internet_check": 1,
                "use_webview2_saml_auth": 0,
                "enable_multi_vpn": 0,
                "enforce_disabling_smartdns": 0,
                "enable_view_selected_vpns": 0,
                "keep_running_max_tries": 0,
                "after_logon_saml_auth": 0,
                "before_logon_saml_auth": 1,
                "allow_personal_vpns": 0,
                "disable_connect_disconnect": 0,
                "autoconnect_on_install": 0,
                "autoconnect_only_when_offnet": 0,
                "temp_password": f"{temp_password}"
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
        #Set correct URL for updating the system profile using the profile ID
        system_profile_update_url = f'{api_url_prefix}/profiles/system/{profile["id"]}/update'
        #Update system profile
        session.put(url=system_profile_update_url, json=system_profile_data, headers=change_headers, verify=False, timeout=30)

#Get VPN profiles
response = session.get(url=vpn_profiles_get_url, headers=api_headers, verify=False, timeout=30)
response_decoded = json.loads(response.content.decode('utf-8'))

for profile in response_decoded['data']['local']:
    if profile['name'] == vpn_profile_name:
        #Set correct URL for updating the VPN profile using the profile ID
        vpn_profile_update_url = f'{api_url_prefix}/profiles/vpn/{profile["id"]}/update'
        #Update VPN profile
        session.put(url=vpn_profile_update_url, json=vpn_profile_data, headers=change_headers, verify=False, timeout=30)

#Perform a logout
session.post(url=logout_url, headers=change_headers, verify=False, timeout=30)
