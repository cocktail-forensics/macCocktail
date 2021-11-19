import os
import plistlib

from datetime import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList, convertTIF
from pathlib import Path

def get_userAccounts(macos_version, report_folder, input_path):

# define artifact location
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# define file name prefixes for user account items
    accountPolicyDataTemplate = report_folder + "accountPolicyData_"
    tifTemplate = report_folder + "tifphoto_"
    accountPolicyDataCount = 1
    tifCount = 1

# define container for results
    data_list = []

# get user accounts
    user_list = getUserList(user_path)

# get user account plists
    final_user_list = []
    for i in user_list:
        final_user_list.append(user_path + i + ".plist")

# get user account details            
    for l in final_user_list:
        name = " "
        description = " "
        realname = " "
        uid = " "
        home = " "
        shell = " "
        hint = " "
        picture = " "
        pnglink = " "
        creation_time = " "
        password_time = " "
        with open(l, "rb") as fp:
            user_plist = plistlib.load(fp)
            for key, val in user_plist.items():
                if key == "name":
                    name = val[0]
                    if len(val) > 1:
                        if "com.apple" not in val[1]:
                            description = val[1]
                elif key == "realname":
                    realname = val[0]
                elif key == "uid":
                    uid = val[0]
                elif key == "home":
                    home = val[0]
                elif key == "shell":
                    shell = val[0]
                elif key == "hint":
                    hint = val[0]
                elif key == "picture":
                    picture = val[0]
                elif key == "accountPolicyData":
                    accountPolicyData = accountPolicyDataTemplate + str(accountPolicyDataCount) + ".plist"
                    with open(accountPolicyData, "wb") as fp2:
                        fp2.write(val[0])
                    accountPolicyDataCount += 1
                    with open(accountPolicyData, "rb") as fp3:
                        accountPolicy_plist = plistlib.load(fp3)
                        for key2, val2 in accountPolicy_plist.items():
                            if key2 == "creationTime":
                                creation_time = datetime.fromtimestamp(val2)
                                creation_time = creation_time.strftime("%Y-%m-%d %H:%M:%S")
                            if key2 == "passwordLastSetTime":
                                password_time = datetime.fromtimestamp(val2)
                                password_time = password_time.strftime("%Y-%m-%d %H:%M:%S")
                elif key == "jpegphoto":
                    tifphoto_path = tifTemplate + str(tifCount) + ".tif"
                    with open(tifphoto_path, "wb") as fp4:
                        fp4.write(val[0])
                    pngphoto = convertTIF(tifphoto_path)
                    tifCount += 1 
                    pnglink = "<img src=\"" + pngphoto + "\"width=60 height=60/>"

        data_list.append((uid,name,description,realname,home,shell,hint,picture,creation_time,password_time,pnglink))
                
# set up reports items
    artifacts = user_path + "*user*.plist"
  
# write HTML report items
    report = ArtifactHtmlReport('User Accounts')
    report.start_artifact_report(report_folder, 'User Accounts')
    report.add_script()
    data_headers = ('UID','Account Name','Description','Real Name','Home Directory','Shell','Hint','Picture', \
        'Creation Time','Password Time','Icon')
    report.write_artifact_data_table(data_headers, data_list, artifacts, html_escape=False)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'User Accounts'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success

