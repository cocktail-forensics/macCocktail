import os
import plistlib
import sqlite3

from datetime import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_systemDetails(macos_version, report_folder, input_path):

# define artifact locations
    systemversion_path = input_path + "/System/Library/CoreServices/SystemVersion.plist"
    if macos_version[:2] == "10":
        serial_path = input_path + "/private/var/folders/zz/zyxvpxvq6csfxvn_n00000sm00006d/C/cache_encryptedA.db"
    elif macos_version[:2] == "11":
        serial_path = input_path + "/private/var/folders/zz/zyxvpxvq6csfxvn_n00000sm00006d/C/locationd/cache_encryptedA.db"
    else:
        serial_path = input_path + "/private/var/folders/zz/zyxvpxvq6csfxvn_n00000sm00006d/C/locationd/cache_encryptedB.db"
    install_path = input_path + "/private/var/db/.AppleSetupDone"
    model_path = input_path + "/Library/Preferences/SystemConfiguration/preferences.plist"
    loginwindow_path = input_path + "/Library/Preferences/com.apple.loginwindow.plist"

# check for valid artifact locations
    artifact_success = 1
    if not os.path.exists(systemversion_path):
        artifact_success = 0
        return artifact_success

# define container for results
    data_list = []

# get product identifiers
    with open(systemversion_path, "rb") as fp:
        systemversion_plist = plistlib.load(fp)
        for key, val in systemversion_plist.items():
            if key == "ProductName":
                logdevinfo(f"ProductName: {val}")
                pname = val                
            elif key == "ProductVersion":
                logdevinfo(f"ProductVersion: {val}")
                pver = val
            elif key == "ProductBuildVersion":
                logdevinfo(f"ProductBuildVersion: {val}")
                pbuild = val

# get serial number
    serial_number = " "

    if os.path.exists(serial_path):
        serial_db = sqlite3.connect(serial_path)
        cursor = serial_db.cursor()
        cursor.execute(
            """
            SELECT
            SerialNumber
            FROM TableInfo
            WHERE TableName == "WifiLocation"
            """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            for row in all_rows:
                logdevinfo(f"SerialNumber: {row[0]}")
                serial_number = row[0]

# get install date
    install_date = " "

    if os.path.exists(install_path):
        i_date = os.path.getatime(install_path)
        install_date = datetime.fromtimestamp(i_date)
        install_date = install_date.strftime("%Y-%m-%d %H:%M:%S")
        logdevinfo(f"InstallDate: {install_date}")


# get model and computer name
    model = " "
    computer_name = " "

    if os.path.exists(model_path):
        with open(model_path, "rb") as fp:
            model_plist = plistlib.load(fp)
            for key, val in model_plist.items():
                if key == "Model":
                    logdevinfo(f"Model: {val}")
                    model = val
                elif key == "System":
                    for i in val:
                        if i == "System":
                            system_attributes = val[i]
                            logdevinfo(f"ComputerName: {system_attributes['ComputerName']}")
                            computer_name = system_attributes['ComputerName']


# get last user details
    guest_enabled = " "
    last_user = " "
    auto_login = " "
    master_password = " "
    auto_password = " "

    if os.path.exists(loginwindow_path):
        with open(loginwindow_path, "rb") as fp:
            loginwindow_plist = plistlib.load(fp)
            for key, val in loginwindow_plist.items():
                if key == "GuestEnabled":
                    logdevinfo(f"GuestEnabled: {val}")
                    guest_enabled = val
                elif key == "lastUserName":
                    logdevinfo(f"lastUserName: {val}")
                    last_user = val
                elif key == "autoLoginUser":
                    logdevinfo(f"autoLoginUser: {val}")
                    auto_login = val
                elif key == "MasterPasswordHint":
                    logdevinfo(f"MasterPasswordHint: {val}")
                    master_password = val

# get auto login password if available
    auto_password = " "
    if auto_login != " ":
        kcpassword_path = input_path + "/etc/kcpassword"
        auto_path = "ruby -e 'key = [125, 137, 82, 35, 210, 188, 221, 234, 163, 185, 31]; IO.read(\"" + kcpassword_path \
            + "\").bytes.each_with_index { |b, i| break if key.include?(b); print [b ^ key[i % key.size]].pack(\"U*\") }'"
        try:
            stream = os.popen(auto_path)
        except:
            stream = " "

        auto_password = stream.read()

# set up report items
    artifacts = systemversion_path + ", " + serial_path + ", " + install_path + ", " \
        + model_path + "," + loginwindow_path
  
# write HTML report items
    report = ArtifactHtmlReport('Mac OS Details')
    report.start_artifact_report(report_folder, 'Mac OS Details')
    report.add_script()
    data_headers = ('Model','Serial Number','Computer Name','Product Name','Product Version', \
        'Product Build','Install Date','Last User','Guest Enabled?','Auto Login User','Auto Login Password','Master Password Hint')
    data_list.append((model,serial_number,computer_name,pname,pver,pbuild,install_date, \
        last_user,guest_enabled,auto_login,auto_password,master_password))
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'Mac OS Details'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
    
