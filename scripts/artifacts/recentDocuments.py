import os
import sys
import shutil
import plistlib
import urllib.parse
import json

from mac_alias import Bookmark
from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList, process_bookmark, getDeserializedPlist

def get_recentDocuments(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    recents_path = "/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    documents_list = []
    for i in user_list:
        documents_list.append(input_path + user_dir + i + recents_path)

# define container for results
    data_list = []

# get document details
    for k in documents_list:
        if os.path.exists(k):
            recent_list = [f for f in os.listdir(k)]
            if len(recent_list) > 0:
                for doc in recent_list:
                    app = doc.split(".sfl2")[0]
                    user = k.split("/")[-5]
                    source_doc = k + "/" + doc
                    deserialized_doc = report_folder + user + "_" + doc + "_deserialized.plist"
                    getDeserializedPlist(source_doc,deserialized_doc,"pfile")
                    with open(deserialized_doc,"rb") as df:
                        app_plist = plistlib.load(df)
                        for key, val in app_plist.items():
                            if key == "items":
                                for attribute in val:
                                    for m, n in attribute.items():
                                        if m == "Bookmark":
                                            if type(n) == bytes:
                                                bookmark = Bookmark.from_bytes(n)
                                            elif type(n) == dict:
                                                bookmark = Bookmark.from_bytes(n["NS.data"])

                                            bookmark_data = process_bookmark(bookmark, input_path)

                                            data_list.append((app,user,bookmark_data[0][0],bookmark_data[0][1],bookmark_data[0][2],bookmark_data[0][3])) 

# set up report items
    artifact = input_path + user_dir + "*user*" + recents_path

# write HTML report items
    report = ArtifactHtmlReport('Recent Documents')
    report.start_artifact_report(report_folder, 'Recent Documents')
    report.add_script()
    data_headers = ('Application','User','Mount Point','Volume Name','Recent Folder','File Creation Date')
    report.write_artifact_data_table(data_headers, data_list, artifact)
    report.end_artifact_report()
    
# write TSV report items
    tsvname = 'Recent Documents'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success

            
