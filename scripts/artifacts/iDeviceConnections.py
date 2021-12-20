import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList 

def get_iDeviceConnections(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    connections_path = "/Library/Preferences/com.apple.iPod.plist"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact locations
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    connected_list = []
    for i in user_list:
        connected_list.append(input_path + user_dir + i + connections_path)

# define container for results 
    data_list = []

# get details for each connection
    for k in connected_list:
        if os.path.exists(k):
            with open(k, "rb") as fp:
                connections_plist = plistlib.load(fp)
                for key, val in connections_plist.items():
                    if key == "Devices":
                        for i in val:
                            device_id = i
                            attributes = val[i]
                            imei = " "
                            device_class = " "
                            serial_number = " "
                            use_count = " "
                            product_type = " "
                            ios_version = " "
                            last_connected = " "
                            for j in attributes:
                                if j == "Device Class":
                                    device_class = attributes[j]
                                elif j == "Serial Number":
                                    serial_number = attributes[j]
                                elif j == "IMEI":
                                    imei = attributes[j]
                                elif j == "Use Count":
                                    use_count = attributes[j]
                                elif j == "Product Type":
                                    product_type = attributes[j]
                                elif j == "Firmware Version String":
                                    ios_version = attributes[j]
                                elif j == "Connected":
                                    last_connected = attributes[j]
                                    last_connected = last_connected.strftime("%Y-%m-%d %H:%M:%S")

                            user = k.split("/")

                            data_list.append((user[-4],device_id,device_class,serial_number,ios_version,imei, \
                                product_type,use_count,last_connected))                            
             
# set up report items
    artifacts = input_path + user_dir + "*users*" + connections_path

# write HTML report items  
    report = ArtifactHtmlReport('iDevice Connections')
    report.start_artifact_report(report_folder, 'iDevice Connections')
    report.add_script()
    data_headers = ('User','Device ID','Device Class','Serial Number','iOS Version','IMEI','Product Type', \
        'Use Count','Last Connected')
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'iDevice Connections'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
            
