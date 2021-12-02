import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv

def get_userAccountsDeleted(macos_version, report_folder, input_path):

# define artifact location
    deleted_users_path = input_path + "/Library/Preferences/com.apple.preferences.accounts.plist"

#check for valid artifact location
    artifact_success = 1
    if not os.path.exists(deleted_users_path):
        artifact_success = 0
        return artifact_success

#define container for results
    data_list = []

#get deleted users
    with open(deleted_users_path, "rb") as fp:
        deleted_users_plist = plistlib.load(fp)
        for key, val in deleted_users_plist.items():      
            if key == "deletedUsers":
                uid = " "
                name = " "
                real_name = " "
                date_deleted = " "
                image_exists = " "
                home_exists = " "
                for user in val:
                    for k in user:
                        if "UniqueID" in k:
                            uid = user[k]
                        elif k == "name":
                            name = user[k]
                            image_path = input_path + "/Users/Deleted Users/" + name + ".dmg"
                            if os.path.exists(image_path):
                                image_exists = "Yes: " + image_path
                            else:
                                image_exists = "No"
                            home_path = input_path + "/Users/" + name + " (Deleted)"
                            if os.path.exists(home_path):
                                home_exists = "Yes: " + home_path
                            else:
                                home_exists = "No" 
                        elif "RealName" in k:
                            real_name = user[k]
                        elif k == "date":
                            date_deleted = user[k]
                            date_deleted = date_deleted.strftime("%Y-%m-%d %H:%M:%S")
 
                    data_list.append((uid,name,"*Deleted Account*",real_name,date_deleted,image_exists,home_exists))

#set up report items
    artifact = deleted_users_path

#write HTML report items
    report = ArtifactHtmlReport('Deleted User Accounts')
    report.start_artifact_report(report_folder, 'Deleted User Accounts')
    report.add_script()
    data_headers = ('UID','Account Name','Description','Real Name','Deleted Date','Image Exists?','Home Dir Exists?')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()

#write TSV report items
    tsvname = 'Deleted User Accounts'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
