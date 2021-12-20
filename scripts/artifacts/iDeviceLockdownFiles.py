import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList

def get_iDeviceLockdownFiles(macos_version, report_folder, input_path):

# define artifact location
    lockdown_path = input_path + "/private/var/db/lockdown/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(lockdown_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get list of lockdown files
    lockdown_list = [f for f in os.listdir(lockdown_path) if ".plist" in f]
    final_lockdown_list = []
    for i in lockdown_list:
        if i != "SystemConfiguration.plist":
            final_lockdown_list.append(lockdown_path + i)   

# get details for each lockdown file            
    for l in final_lockdown_list:
        uuid = " "
        host_id = " "
        mac_address = " "
        system_buid = " "
        with open(l, "rb") as fp:
            lockdown_plist = plistlib.load(fp)
            uuid = l.split("/")
            lockdown_file = uuid[-1]
            for key, val in lockdown_plist.items():
                if key == "HostID":
                    host_id = val
                elif key == "SystemBUID":
                    system_buid = val
                elif "MACAddress" in key:
                    mac_address = val.upper()

        data_list.append((lockdown_file,host_id,system_buid,mac_address))
  
# set up report items
    artifact = lockdown_path + "*.plist"

# write HTML report items
    report = ArtifactHtmlReport('iDevice Lockdown Files')
    report.start_artifact_report(report_folder, 'iDevice Lockdown Files')
    report.add_script()
    data_headers = ('Lockdown File (UDID of Device)','Host ID','System BUID','MAC Address')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()
    
# write TSV report items    
    tsvname = 'iDevice Lockdown Files'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
            
