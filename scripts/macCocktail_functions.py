import csv
import datetime
import os
import pathlib
import plistlib
import sys
import codecs
import json
import glob
import nska_deserialize as nd

from mac_alias import Bookmark
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image

#screen_output_file_path_devinfo = os.path.join(reportfolderbase, 'Script Logs', 'DeviceInfo.html')
class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''

    def __init__(self, output_folder):
        now = datetime.datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder, 'macCocktail_Reports_' + currenttime)
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs', 'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs', 'DeviceInfo.html')

        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

def getUserList(user_path):
    full_user_list = [f for f in os.listdir(user_path) if ".plist" in f]
    final_user_list = []

    for i in full_user_list:
        if i[0] != "_":  #and "nobody" not in i and "daemon" not in i:
            split_list = i.split(".")
            final_user_list.append(split_list[0])   
    return final_user_list

class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None # static variable 
    progress_bar_total = 0
    progress_bar_handle = None

    @staticmethod
    def SetProgressBar(n):
        if GuiWindow.progress_bar_handle:
            GuiWindow.progress_bar_handle.UpdateBar(n)
            
def logfunc(message=""):
    with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
        print(message)
        a.write(message + '<br>' + OutputParameters.nl)

    if GuiWindow.window_handle:
        GuiWindow.window_handle.refresh()

def logdevinfo(message=""):
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        b.write(message + '<br>' + OutputParameters.nl)
    
def html2csv(reportfolderbase):
    #List of items that take too long to convert or that shouldn't be converted
    itemstoignore = ['index.html',
                    'Distribution Keys.html', 
                    'StrucMetadata.html',
                    'StrucMetadataCombined.html']
                    
    if os.path.isdir(os.path.join(reportfolderbase, '_CSV Exports')):
        pass
    else:
        os.makedirs(os.path.join(reportfolderbase, '_CSV Exports'))
    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        for file in files:
            if file.endswith(".html"):
                fullpath = (os.path.join(root, file))
                head, tail = os.path.split(fullpath)
                if file in itemstoignore:
                    pass
                else:
                    data = open(fullpath, 'r', encoding='utf8')
                    soup=BeautifulSoup(data,'html.parser')
                    tables = soup.find_all("table")
                    data.close()
                    output_final_rows=[]

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll('tr'):

                            columns = table_row.findAll('td')
                            output_row = []
                            for column in columns:
                                    output_row.append(column.text)
                            output_rows.append(output_row)
        
                        file = (os.path.splitext(file)[0])
                        with codecs.open(os.path.join(reportfolderbase, '_CSV Exports',  file +'.csv'), 'a', 'utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
                            writer.writerows(output_rows)

def tsv(report_folder, data_headers, data_list, tsvname):
    report_folder = report_folder.rstrip('/')
    report_folder_base, tail = os.path.split(report_folder)
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')
    
    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)
    
    
    with codecs.open(os.path.join(tsv_report_folder + '/' + tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter='\t')
        tsv_writer.writerow(data_headers)
        for i in data_list:
            tsv_writer.writerow(i)

def convertTIF(tif_photopath):
    outfile = os.path.splitext(os.path.join(tif_photopath))[0] + ".png"

    im = Image.open(os.path.join(tif_photopath))
    im.thumbnail(im.size)
    im.save(outfile, "PNG", quality=100)

    return outfile

def getModel(model_id):
    full_model = "Unresolved"
    model_list = {
        'X' : 'X'
    }

    return full_model

def getRecursiveList(directory):
    recursive_list = []

    files = glob.glob(directory, recursive=True)
    for name in files:
        recursive_list.append(name)

    return recursive_list

def get_macos_version(input_path):
    systemversion_path = input_path + "/System/Library/CoreServices/SystemVersion.plist"
    if not os.path.exists(systemversion_path):
        macos_version = 0
        return macos_version

    with open(systemversion_path, "rb") as fp:
        systemversion_plist = plistlib.load(fp)
        for key, val in systemversion_plist.items():              
            if key == "ProductVersion":
                logdevinfo(f"ProductVersion: {val}")
                macos_version = val

    return macos_version

def process_bookmark(bookmark, input_path):
    bookmark_data = []
    name = " "
    creation_date = " "
    volume_name = " "
    mount_name = " "
    book_items = vars(bookmark)
    for toc in book_items:
        name_count = 1
        create_count = 1
        vol_count = 1
        mount_count = 1
        for tups in book_items[toc]:
            tups_dict = tups[1]
            for item in tups_dict:
                if item == 4100:
                    if name_count == 1:
                        name = input_path + "/" + '/'.join(tups_dict[item])
                        name_count += 1
                elif item == 4160:
                    if create_count == 1:
                        creation_date = tups_dict[item]
                        creation_date = creation_date.strftime("%Y-%m-%d %H:%M:%S")
                        create_count += 1
                elif item == 8208:
                    if vol_count == 1:
                        volume_name = tups_dict[item]
                        vol_count += 1
                elif item == 8194:
                    if mount_count == 1:
                        mount_name = tups_dict[item]
                        mount_count += 1

    bookmark_data.append((mount_name,volume_name,name,creation_date))
    return bookmark_data

def getDeserializedPlist(nska_plist,output_file,ftype):
    with open(nska_plist, 'rb') as f:
        try:
            deserialized_plist = nd.deserialize_plist(f)
        except (nd.DeserializeError, 
                nd.biplist.NotBinaryPlistException, 
                nd.biplist.InvalidPlistException,
                nd.ccl_bplist.BplistError, 
                ValueError, TypeError, OSError, OverflowError) as ex:
            # These are all possible errors from libraries imported

            print('Had exception: ' + str(ex))
            deserialized_plist = "None"

        if ftype == "pfile":
            nd.write_plist_to_file(deserialized_plist,output_file)
        else:
            nd.write_plist_to_json_file(deserialized_plist,output_file)

def config_details(account_type, account_id, details_rows, report_folder):
    details = []
    if account_type == "Apple ID":
        for row in details_rows:
            if row[1] == "Apple ID" and row[4] == "dsid" and row[0] == account_id:
                dsid = " "
                details_plist = report_folder + "apple_id_dsid.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                dsid_file = report_folder + "apple_id_dsid.plist_deserialized.json"
                getDeserializedPlist(details_plist,dsid_file,"jfile")
                with open(dsid_file,"r") as af:
                    dsid_json = json.load(af)
                    for key, val in dsid_json.items():
                        if key == "root":
                            dsid = "DSID: " + val
                            details.append(dsid)

        for p in Path(report_folder).glob("apple_id_dsid.*"):
            p.unlink()

    elif account_type == "Messages":
        for row in details_rows:
            if row[1] == "Messages" and row[4] == "profile-id" and row[0] == account_id:
                profile_id = " "
                details_plist = report_folder + "messages_profile_id.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                messages_file = report_folder + "messages_profile_id.plist_deserialized.json"
                getDeserializedPlist(details_plist,messages_file,"jfile") 
                with open(messages_file,"r") as af:
                    messages_json = json.load(af)
                    for key, val in messages_json.items():
                        if key == "root":
                            profile_id = "Profile ID: " + val.split(":")[-1]
                            details.append(profile_id)
            elif row[1] == "Messages" and row[4] == "invitation-context" and row[0] == account_id:
                region_id = " "
                details_plist = report_folder + "messages_invitation_context.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                messages_file = report_folder + "messages_invitation_context.plist_deserialized.json"
                getDeserializedPlist(details_plist,messages_file,"jfile")
                with open(messages_file,"r") as af:
                    messages_json = json.load(af)
                    for key, val in messages_json.items():
                        if key == "region-id":
                            region_id = "Region ID: " + val.split(":")[-1]
                            details.append(region_id)
            elif row[1] == "Messages" and row[4] == "account-info" and row[0] == account_id:
                messages_info = []
                details_plist = report_folder + "messages_account_info.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                messages_file = report_folder + "messages_account_info.plist_deserialized.json"
                getDeserializedPlist(details_plist,messages_file,"jfile")
                with open(messages_file,"r") as af:
                    messages_json = json.load(af)
                    for key, val in messages_json.items():
                        if key == "VettedAliases":
                            for alias in val:
                                messages_info.append(alias)
                            aliases = "Aliases: " + ', '.join(messages_info)
                            details.append(aliases)

        for p in Path(report_folder).glob("messages_profile_id.*"):
            p.unlink()
        for p in Path(report_folder).glob("messages_invitation_context.*"):
            p.unlink()
        for p in Path(report_folder).glob("messages_account_info.*"):
            p.unlink()

    elif account_type == "CalDAV":
        for row in details_rows:
            if row[1] == "CalDAV" and row[4] == "kCalDAVPrincipalsKey" and row[0] == account_id:
                full_name = " "
                details_plist = report_folder + "caldav_full_name.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                caldav_file = report_folder + "caldav_full_name.plist_deserialized.json"
                getDeserializedPlist(details_plist,caldav_file,"jfile")
                with open(caldav_file,"r") as af:
                    caldav_json = json.load(af)
                    for key, val in caldav_json.items():
                        for id in val:
                            if id == "ACPropertyFullName":
                                full_name = "Full Name: " + val[id]
                                details.append(full_name)

        for p in Path(report_folder).glob("caldav_full_name.*"):
            p.unlink()

    elif account_type == "CardDAV":
        for row in details_rows:
            if row[1] == "CardDAV" and row[4] == "PrincipalInfo" and row[0] == account_id:
                display_name = " "
                details_plist = report_folder + "carddav_display_name.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                carddav_file = report_folder + "carddav_display_name.plist_deserialized.json"
                getDeserializedPlist(details_plist,carddav_file,"jfile")
                with open(carddav_file,"r") as af:
                    carddav_json = json.load(af)
                    for key, val in carddav_json.items():
                        if key == "DAV::displayname":
                            display_name = "Display Name: " + val
                            details.append(display_name)

        for p in Path(report_folder).glob("carddav_display_name.*"):
            p.unlink()

    elif account_type == "Gmail":
        for row in details_rows:
            if row[1] == "Gmail" and row[4] == "ACPropertyFullName" and row[0] == account_id:
                full_name = " "
                details_plist = report_folder + "gmail_full_name.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                gmail_file = report_folder + "gmail_full_name.plist_deserialized.json"
                getDeserializedPlist(details_plist,gmail_file,"jfile")
                with open(gmail_file,"r") as af:
                    gmail_json = json.load(af)
                    for key, val in gmail_json.items():
                        if key == "root":
                            full_name = "Full Name: " + val
                            details.append(full_name)

        for p in Path(report_folder).glob("gmail_full_name.*"):
            p.unlink()

    elif account_type == "iCloud":
        for row in details_rows:
            if row[1] == "iCloud" and row[4] == "AccountDelegate" and row[0] == account_id:
                full_name = " "
                dsid = " "
                apple_id = " "
                details_plist = report_folder + "icloud_account_delegate.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                icloud_file = report_folder + "icloud_account_delegate.plist_deserialized.json"
                getDeserializedPlist(details_plist,icloud_file,"jfile")
                with open(icloud_file,"r") as af:
                    icloud_json = json.load(af)
                    for key, val in icloud_json.items():
                        if key == "appleAccountInfo":
                            for k, v in val.items():

                                if k == "appleId":
                                    apple_id = "Apple ID: " + v
                                    details.append(apple_id)
                                elif k == "dsPrsID":
                                    dsid = "DSID: " + v
                                    details.append(dsid)
                                elif k == "fullName":
                                    full_name = "Full Name: " + v
                                    details.append(full_name)

        for p in Path(report_folder).glob("icloud_account_delegate.*"):
            p.unlink()

    elif account_type == "IMAP":
        for row in details_rows:
            if row[1] == "IMAP" and row[4] == "EmailAliases" and row[0] == account_id:
                display_name = " "
                email_address = " "
                details_plist = report_folder + "imap_email_addresses.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                imap_file = report_folder + "imap_email_addresses.plist_deserialized.json"
                getDeserializedPlist(details_plist,imap_file,"jfile")
                with open(imap_file,"r") as af:
                    imap_json = json.load(af)
                    for key, val in imap_json[0].items():
                        if key == "DisplayName":
                            display_name = "Display Name: " + val
                            details.append(display_name)
                        elif key == "EmailAddresses":
                            for k, v in val[0].items():
                                if k == "EmailAddress":
                                    email_address = "Email Address: " + v
                                    details.append(email_address)

        for p in Path(report_folder).glob("imap_email_addresses.*"):
            p.unlink()

    elif account_type == "SMTP":
        for row in details_rows:
            if row[1] == "SMTP" and row[4] == "IdentityEmailAddress" and row[0] == account_id:
                email_address = " "
                details_plist = report_folder + "smtp_email_address.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                smtp_file = report_folder + "smtp_email_address.plist_deserialized.json"
                getDeserializedPlist(details_plist,smtp_file,"jfile")
                with open(smtp_file,"r") as af:
                    smtp_json = json.load(af)
                    for key, val in smtp_json.items():
                        if key == "root":
                            email_address = "Email Address: " + val
                            details.append(email_address)
            elif row[1] == "SMTP" and row[4] == "Hostname" and row[0] == account_id:
                hostname = " "
                details_plist = report_folder + "smtp_hostname.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                smtp_file = report_folder + "smtp_hostname.plist_deserialized.json"
                getDeserializedPlist(details_plist,smtp_file,"jfile")
                with open(smtp_file,"r") as af:
                    smtp_json = json.load(af)
                    for key, val in smtp_json.items():
                        if key == "root":
                            hostname = "Hostname: " + val
                            details.append(hostname)


        for p in Path(report_folder).glob("smtp_email_address.*"):
            p.unlink()
        for p in Path(report_folder).glob("smtp_hostname.*"):
            p.unlink()

    elif account_type == "IDMS":
        for row in details_rows:
            if row[1] == "IDMS" and row[4] == "DSID" and row[0] == account_id:
                dsid = " "
                details_plist = report_folder + "idms_dsid.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                idms_file = report_folder + "idms_dsid.plist_deserialized.json"
                getDeserializedPlist(details_plist,idms_file,"jfile")
                with open(idms_file,"r") as af:
                    idms_json = json.load(af)
                    for key, val in idms_json.items():
                        if key == "root":
                            dsid = "DSID: " + val
                            details.append(dsid)
            elif row[1] == "IDMS" and row[4] == "aliases" and row[0] == account_id:
                aliases_list = []
                aliases = " "
                details_plist = report_folder + "idms_aliases.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                idms_file = report_folder + "idms_aliases.plist_deserialized.json"
                getDeserializedPlist(details_plist,idms_file,"jfile")
                with open(idms_file,"r") as af:
                    idms_json = json.load(af)
                    for val in idms_json:
                        aliases_list.append(val)
                    aliases = "Aliases: " + ', '.join(aliases_list)
                    details.append(aliases)

        for p in Path(report_folder).glob("idms_dsid.*"):
            p.unlink()
        for p in Path(report_folder).glob("idms_aliases.*"):
            p.unlink()

    elif account_type == "Game Center":
        for row in details_rows:
            if row[1] == "Game Center" and row[4] == "playerID" and row[0] == account_id:
                player_id = " "
                details_plist = report_folder + "game_player_id.plist"
                with open(details_plist, "wb") as fp:
                    fp.write(row[5])
                gc_file = report_folder + "game_player_id.plist_deserialized.json"
                getDeserializedPlist(details_plist,gc_file,"jfile")
                with open(gc_file,"r") as af:
                    gc_json = json.load(af)
                    for key, val in gc_json.items():
                        if key == "root":
                            player_id = "Player ID: " + val.split(":")[-1]
                            details.append(player_id)

        for p in Path(report_folder).glob("game_player_id.*"):
            p.unlink()

    if len(details) > 0:
        final_details = ' | '.join(details)
    else:
        final_details = " " 
    return(final_details)



