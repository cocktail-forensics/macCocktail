import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_networkHistory(macos_version, report_folder, input_path):

# define artifact location
    history_path = input_path + "/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(history_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get network history
    with open(history_path, "rb") as fp:
        history_plist = plistlib.load(fp)
        for key, val in history_plist.items():

            if key == "KnownNetworks":
                for i in val:
                    wifi_id = i
                    attributes = val[i]
                    ssid_string = " "
                    added_by = " "
                    captive = " "
                    captive_bypass = " "
                    security_type = " "
                    share_mode = " "
                    user_role = " "
                    last_connected = " "
                    roaming_type = " "
                    bssid = " "
                    bssid_list = []
                    for k in attributes:
                        if k == "SSIDString":
                            ssid_string = attributes[k]
                        elif k == "AddedBy":
                            added_by = attributes[k]
                        elif k == "Captive":
                            captive = attributes[k]
                        elif k == "CaptiveBypass":
                            captive_bypass = attributes[k]
                        elif k == "SecurityType":
                            security_type = attributes[k]
                        elif k == "ShareMode":
                            share_mode = attributes[k]
                        elif k == "UserRole":
                            user_role = attributes[k]
                        elif k == "LastConnected":
                            last_connected = attributes[k]
                        elif k == "RoamingProfileType":
                            roaming_type = attributes[k]
                        elif k == "BSSIDList":
                            for l in attributes[k]:
                                for m in l:
                                    if m == "LEAKY_AP_BSSID":
                                        bssid_list.append(l[m].upper())
                                bssid = ', '.join(bssid_list)

                    data_list.append((ssid_string,security_type,roaming_type,bssid, \
                        last_connected,added_by,captive,captive_bypass,share_mode,user_role))                            
              
# set up report items
    artifact = history_path

# write HTML report items  
    report = ArtifactHtmlReport('Network History')
    report.start_artifact_report(report_folder, 'Network History')
    report.add_script()
    data_headers = ('SSID','Security Type','Roaming Type','BSSID(s)','Last Connected','Added By','Captive?','Captive Bypass?', \
        'Share Mode','User Role')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'Network History'
    tsv(report_folder, data_headers, data_list, tsvname)
    
    return artifact_success
            
