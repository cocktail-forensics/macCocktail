import os
import plistlib
import binascii

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_networkConfiguration(macos_version, report_folder, input_path):

# define artifact location
    configuration_path = input_path + "/Library/Preferences/SystemConfiguration/preferences.plist"
    dhcp_path = input_path + "/private/var/db/dhcpclient/leases"

# check for valid artifact locations
    artifact_success = 1
    if not os.path.exists(configuration_path) and not os.path.exists(dhcp_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get dhcp lease list
    dhcp_list = [f for f in os.listdir(dhcp_path)]

# get network configuration
    with open(configuration_path, "rb") as fp:
        configuration_plist = plistlib.load(fp)
        for key, val in configuration_plist.items():
            if key == "NetworkServices":
                for i in val:
                    net_id = i
                    attributes = val[i]
                    config_method = " "
                    ip_address = " "
                    lease_start = " "
                    router_mac = " "
                    router_address = " "
                    ssid_name = " "
                    hardware = " "
                    net_type = " "
                    net_name = " "
                    for j in attributes:
                        if j == "IPv4":
                            k = attributes[j]
                            for l in k:
                                if l == "ConfigMethod":                      
                                    config_method = k[l]
                        elif j == "Interface":
                            k = attributes[j]
                            for l in k:
                                if l == "DeviceName":                      
                                    device_name = k[l]
                                    for dhcp in dhcp_list:
                                        if device_name in dhcp:
                                            full_dhcp_path = dhcp_path + "/" + dhcp
                                            with open(full_dhcp_path, "rb") as fp:
                                                dhcp_plist = plistlib.load(fp)
                                                for m, n in dhcp_plist.items():
                                                    if m == "IPAddress":                      
                                                        ip_address = n
                                                    elif m == "LeaseStartDate":                      
                                                        lease_start = n                                                 
                                                    elif m == "RouterHardwareAddress":                      
                                                        rm = binascii.hexlify(n)
                                                        rm = rm.decode("ascii").upper()
                                                        router_mac = ':'.join(rm[i:i+2] for i in range(0,12,2))
                                                    elif m == "RouterIPAddress":                      
                                                        router_address = n
                                                    elif m == "SSID":                      
                                                        ssid_name = n

                                elif l == "Hardware":                      
                                    hardware = k[l]   
                                elif l == "Type":                      
                                    net_type = k[l]    
                                elif l == "UserDefinedName":                      
                                    net_name = k[l]        

                    data_list.append((device_name,net_id,net_name,hardware,net_type,config_method, \
                        ip_address,ssid_name,router_address,router_mac,lease_start))                            

# set up report items
    artifacts = configuration_path + ", " + dhcp_path

# write HTML report items
    report = ArtifactHtmlReport('Network Configuration')
    report.start_artifact_report(report_folder, 'Network Configuration')
    report.add_script()
    data_headers = ('Device','ID','Name','Hardware','Type','Config Method','IP Address', \
        'SSID','Router IP Address','Router MAC Address','Lease Start Date')
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()

# write TSV report items     
    tsvname = 'Network Configuration'
    tsv(report_folder, data_headers, data_list, tsvname)
    
    return artifact_success
            
