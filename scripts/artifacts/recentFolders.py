import os
import plistlib
import urllib.parse

from mac_alias import Bookmark
from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList, process_bookmark

def get_recentFolders(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    recents_path = "/Library/Preferences/com.apple.finder.plist"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    folders_list = []
    for i in user_list:
        folders_list.append(input_path + user_dir + i + recents_path)

# define container for results
    data_list = []

# get folder details
    for k in folders_list:
        if os.path.exists(k):
            recent_folder = " "
            with open(k, "rb") as fp:
                recent_plist = plistlib.load(fp)
                for key, val in recent_plist.items():
                    if key == "FXRecentFolders":
                        for attribute in val:
                            short_name = attribute["name"]
                            bookmark = Bookmark.from_bytes(attribute["file-bookmark"])
                            bookmark_data = process_bookmark(bookmark, input_path)

                            user = k.split("/")

                            data_list.append((user[-4],bookmark_data[0][0],bookmark_data[0][1],bookmark_data[0][2],bookmark_data[0][3]))                           

# set up report items   
    artifact = input_path + user_dir + "*user*" + recents_path

# write HTML report items
    report = ArtifactHtmlReport('Recent Folders')
    report.start_artifact_report(report_folder, 'Recent Folders')
    report.add_script()
    data_headers = ('User','Mount Point','Volume Name','Recent Folder','Folder Creation Date')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()

# write TSV report items    
    tsvname = 'Recent Folders'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
        
