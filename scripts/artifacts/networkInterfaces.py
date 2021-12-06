import os
import plistlib
import binascii

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_networkInterfaces(macos_version, report_folder, input_path):

# define artifact location
    interfaces_path = input_path + "/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(interfaces_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get network interfaces
    with open(interfaces_path, "rb") as fp:
        interfaces_plist = plistlib.load(fp)
        for key, val in interfaces_plist.items():
            if key == "Interfaces":
                for items in val:
                    active = "False"
                    interface_id = " "
                    mac_address = " "
                    interface_type = " "
                    interface_name = " "
                    for k in items:
                        if k == "Active":
                            active = items[k]
                        elif k == "BSD Name":
                            interface_id = items[k]
                        elif k == "IOMACAddress":
                            mac = binascii.hexlify(bytearray(items[k])).decode("ascii")
                            mac_address = ':'.join(mac[i:i+2] for i in range(0,12,2))
                        elif k == "SCNetworkInterfaceType":
                            interface_type = items[k]
                        elif k == "SCNetworkInterfaceInfo":
                            for l in items[k]:
                                if l == "UserDefinedName":
                                    interface_name = items[k][l]

                    data_list.append((interface_id,interface_name,interface_type,active,mac_address.upper()))                                         

# set up report items
    artifact = interfaces_path

# write HTML report items
    report = ArtifactHtmlReport('Network Interfaces')
    report.start_artifact_report(report_folder, 'Network Interfaces')
    report.add_script()
    data_headers = ('ID', 'Name', 'Type', 'Active', 'MAC Address')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'Network Interfaces'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
            