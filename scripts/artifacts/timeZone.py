import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_timeZone(macos_version, report_folder, input_path):

#define artifact locations
    timezone_path = input_path + "/private/etc/localtime"
    timezone_details_path = input_path + "/Library/Preferences/.GlobalPreferences.plist"
    if macos_version[:5] == "10.14":
        timezone_auto_path = input_path + "/private/var/db/timed/Library/Preferences/com.apple.timed.plist"
    else:
        timezone_auto_path = input_path + "/Library/Preferences/com.apple.timezone.auto.plist"
    time_server_path = input_path + "/private/etc/ntp.conf"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(timezone_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get timezone
    timezone = os.readlink(timezone_path).split("zoneinfo/")[-1]
    logdevinfo(f"Time Zone: {timezone}")

# get timezone details
    with open(timezone_details_path, "rb") as fp:
        timezone_plist = plistlib.load(fp)
        tcity = " "
        tcountry = " "
        tcoords = " "
        for key, val in timezone_plist.items():        
            if key == "com.apple.TimeZonePref.Last_Selected_City":
                logdevinfo(f"City: {val[5]}")
                tcity = val[5]
                logdevinfo(f"Country: {val[4]}")
                tcountry = val[4]
                tcoords = val[0] + ", " + val[1]
                logdevinfo(f"Coordinates: {tcoords}")

# get timezone auto settings
    with open(timezone_auto_path, "rb") as fp:
        timezone_plist = plistlib.load(fp)
        autozone = " "
        autotime = " "
        for key, val in timezone_plist.items():        
            if key == "TMAutomaticTimeZoneEnabled":
                logdevinfo(f"Auto Time Zone Set: {val}")
                autozone = val
            elif key == "Active":
                logdevinfo(f"Auto Time Zone Set: {val}")
                autozone = val               
            elif key == "TMAutomaticTimeOnlyEnabled":
                logdevinfo(f"Auto Time Set: {val}")
                autotime = val

# get time server
    timeserver = " "
    fp = open(time_server_path, "r")
    lines = fp.readlines()
    timeserver = ','.join(lines)

# set up report items
    artifacts = timezone_path + ", " + timezone_details_path + ", " + timezone_auto_path + ", " + time_server_path

# write HTML report items
    report = ArtifactHtmlReport('Time Zone')
    report.start_artifact_report(report_folder, 'Time Zone')
    report.add_script()
    data_headers = ('Time Zone','City','Country','Coordinates','Auto Time Zone Set','Auto Time Set','Time Server')
    data_list.append((timezone,tcity,tcountry,tcoords,autozone,autotime,timeserver))
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()
    
#write TSV report items 
    tsvname = 'Time Zone'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
    
        