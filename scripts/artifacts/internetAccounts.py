import os
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.macCocktail_functions import logdevinfo, tsv, getUserList, config_details
from distutils.dir_util import copy_tree
from pathlib import Path

def get_internetAccounts(macos_version, report_folder, input_path):

# define artifact locations
    user_dir = "/Users/"
    config_path = "/Library/Accounts/Accounts4.sqlite"
    user_path = input_path + "/private/var/db/dslocal/nodes/Default/users/"

# check for valid artifact locations
    artifact_success = 1
    if not os.path.exists(user_path):
        artifact_success = 0
        return artifact_success

# get user accounts
    user_list = getUserList(user_path)
    config_list = []
    for i in user_list:
        config_list.append(input_path + user_dir + i + config_path)

# define container for results  
    data_list = []

# get internet account details for each account
    for k in config_list:
        if os.path.exists(k):
            split_filedir = k.split("/")
            split_filedir.pop()
            clean_filedir = '/'.join(split_filedir)
            copy_tree(clean_filedir, report_folder)
            config_file = report_folder + "Accounts4.sqlite"
            config_db = sqlite3.connect(config_file)
            cursor = config_db.cursor()
            cursor.execute(
                """
                SELECT
                ZACCOUNTTYPE.ZACCOUNTTYPEDESCRIPTION as 'Account Type',
                ZACCOUNTTYPE.ZIDENTIFIER as 'Account Identifier',
                ZACCOUNT.ZACCOUNTDESCRIPTION as 'Account Description',
                ZACCOUNT.ZUSERNAME as 'Account Username',
                DATETIME(ZACCOUNT.ZDATE+978307200,'UNIXEPOCH') AS 'Account Setup',
                ZACCOUNT.ZIDENTIFIER as 'GUID',
                ZACCOUNT.Z_PK as 'ID'
                FROM ZACCOUNT
                LEFT JOIN ZACCOUNTTYPE ON ZACCOUNT.ZACCOUNTTYPE == ZACCOUNTTYPE.Z_PK
                """
            )

            config_rows = cursor.fetchall()
            usageentries = len(config_rows)

            cursor.execute(
                """
                SELECT
                ZACCOUNT.Z_PK as'ID',
                ZACCOUNTTYPE.ZACCOUNTTYPEDESCRIPTION as 'Account Type',
                ZACCOUNT.ZUSERNAME as 'Account Username',
                ZACCOUNT.ZACCOUNTDESCRIPTION as 'Account Description',
                ZACCOUNTPROPERTY.ZKEY as 'Config Key',
                ZACCOUNTPROPERTY.ZVALUE as 'Config Data'
                FROM ZACCOUNTPROPERTY
                LEFT JOIN ZACCOUNT ON ZACCOUNT.Z_PK == ZACCOUNTPROPERTY.ZOWNER
                LEFT JOIN ZACCOUNTTYPE ON ZACCOUNT.ZACCOUNTTYPE == ZACCOUNTTYPE.Z_PK
                """
            )

            details_rows = cursor.fetchall()

            if usageentries > 0:
                for row in config_rows:
                    account_type = row[0]
                    account_identifier = row[1]
                    account_description = row[2]
                    account_username = row[3]
                    account_setup = row[4]
                    guid = row[5]

                    details = config_details(row[0], row[6], details_rows, report_folder)

                    user = k.split("/")

                    data_list.append((account_type,account_identifier,user[-4],account_description, \
                        account_username,account_setup,guid,details))

            for p in Path(report_folder).glob("Accounts4.*"):
                p.unlink()

# set up report items
    artifacts = input_path + user_dir + "*users*" + config_path

# write HTML report items
    report = ArtifactHtmlReport('Internet Accounts')
    report.start_artifact_report(report_folder, 'Internet Accounts')
    report.add_script()
    data_headers = ('Account Type','Account Identifier','User','Account Description','Account Username', \
        'Account Setup Date','GUID','Details')
    report.write_artifact_data_table(data_headers, data_list, artifacts)
    report.end_artifact_report()

# write TSV report items
    tsvname = 'Internet Accounts Configuration'
    tsv(report_folder, data_headers, data_list, tsvname)

    return artifact_success
            
