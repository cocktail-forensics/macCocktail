import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList 

def get_iDeviceBackups(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    backup_path = "/Library/Application Support/MobileSync/Backup/"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    backup_list = []
    for i in user_list:
        backup_list.append(input_path + user_dir + i + backup_path)

# define container for results
    data_list = []

# get details for each backup
    for backup_dir in backup_list:
        if os.path.exists(backup_dir):
            udid_list = os.listdir(backup_dir)
            for udid in udid_list:
                if os.path.isdir(backup_dir+udid):
                    udid_id = udid
                    phone_number = " "
                    imei = " "
                    device_name = " "
                    product_name = " "
                    serial_number = " "
                    guid = " "
                    iccid = " "
                    product_type = " "
                    ios_version = " "
                    last_backup = " "
                    is_encrypted = " "
                    passcode = " "
                    with open(backup_dir+udid_id+"/Info.plist", "rb") as fp:
                        info_plist = plistlib.load(fp)
                        for key, val in info_plist.items():
                            if key == "Device Name":
                                device_name = val
                            elif key == "Product Name":
                                product_name = val
                            elif key == "Serial Number":
                                serial_number = val
                            elif key == "GUID":
                                guid = val
                            elif key == "ICCID":
                                iccid = val
                            elif key == "IMEI":
                                imei = val
                            elif key == "Phone Number":
                                phone_number = val
                            elif key == "Product Type":
                                product_type = val
                            elif key == "Product Version":
                                ios_version = val
                            elif key == "Last Backup Date":
                                last_backup = val
                    with open(backup_dir+udid_id+"/Manifest.plist", "rb") as fp:
                        manifest_plist = plistlib.load(fp)
                        for key, val in manifest_plist.items():
                            if key == "IsEncrypted":
                                is_encrypted = val
                            elif key == "WasPasscodeSet":
                                passcode = val

                    user = backup_dir.split("/")

                    data_list.append((udid_id,user[-6],device_name,product_name,product_type,serial_number, \
                        ios_version,phone_number,guid,iccid,imei,last_backup,is_encrypted,passcode))     
                
 
# set up report items   
    artifacts = input_path + user_dir + "*user*" + backup_path + "*udid*/Info.plist" + ", " + \
        input_path + user_dir + "*user*" + backup_path + "*udid*/Manifest.plist"

# write HTML report items
    report = ArtifactHtmlReport('iDevice Backups')
    report.start_artifact_report(report_folder, 'iDevice Backups')
    report.add_script()
    data_headers = ('UDID','User','Device Name','Product Name','Product Type','Serial Number','iOS Version', \
        'Phone Number','GUID','ICCID','IMEI','Last Backup Date','Was Backup Encrypted?','Was Passcode Set?')
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()
    
# write TSV report items
    tsvname = 'iDevice Backups'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success           
