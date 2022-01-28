import os
import xattr
import biplist
import binascii

from datetime import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList, getRecursiveList

def get_downloadAttributes(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    downloads_path = "/Downloads"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact location
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    download_list = []
    for i in user_list:
        download_list.append(input_path + user_dir + i + downloads_path)

# define container for results
    data_list = []

# get download attributes
    for download_path in download_list:
        user = download_path.split("/")[-2]
        recursive_list = getRecursiveList(download_path + "/**/*.*")
        for download_file in recursive_list:
            attribute = xattr.xattr(download_file)

            try:
                where_froms = biplist.readPlistFromString(attribute.get("com.apple.metadata:kMDItemWhereFroms"))
            except:
                where_froms = " "

            combined_froms = '<br>'.join(where_froms)

            try:
                quarantine = attribute.get("com.apple.quarantine").decode("utf-8").split(";")
            except:
                quarantine = " "

            if quarantine != " ":
                application = quarantine[2]
                q_int = int(quarantine[1],16)
                q_date = datetime.fromtimestamp(q_int).strftime("%Y-%m-%d %H:%M:%S")
            else:
                application = " "
                q_date = " "

#            if where_froms != " ":
            data_list.append((download_file,user,application,q_date,combined_froms))                      

# set up report items
    artifact = input_path + user_dir + "*user*" + downloads_path

# write HTML report items 
    report = ArtifactHtmlReport('Downloads Extended Attributes')
    report.start_artifact_report(report_folder, 'Downloads Extended Attributes')
    report.add_script()
    data_headers = ('Download File','User','Application Used','Download or Last Save Date','Where Froms',)
    report.write_artifact_data_table(data_headers, data_list, artifact, html_escape=False)
    report.end_artifact_report()

# write TSV report items
    tsvname = 'Downloads Extended Attributes'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
