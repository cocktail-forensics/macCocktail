# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.systemDetails import get_systemDetails
from scripts.artifacts.timeZone import get_timeZone
from scripts.artifacts.userAccounts import get_userAccounts
from scripts.artifacts.userAccountsDeleted import get_userAccountsDeleted
from scripts.artifacts.networkInterfaces import get_networkInterfaces
from scripts.artifacts.networkConfiguration import get_networkConfiguration
from scripts.artifacts.networkHistory import get_networkHistory
# from scripts.artifacts.internetAccounts import get_internetAccounts
# from scripts.artifacts.internetAccountsConfiguration import get_internetAccountsConfiguration
# from scripts.artifacts.iDeviceConnections import get_iDeviceConnections
# from scripts.artifacts.iDevicelockdownFiles import get_iDevicelockdownFiles
# from scripts.artifacts.iDeviceBackups import get_iDeviceBackups
# from scripts.artifacts.officeExcelMRUs import get_officeExcelMRUs
# from scripts.artifacts.officeWordMRUs import get_officeWordMRUs
# from scripts.artifacts.officePowerPointMRUs import get_officePowerPointMRUs
# from scripts.artifacts.recentFolders import get_recentFolders
# from scripts.artifacts.recentDocuments import get_recentDocuments
# from scripts.artifacts.downloadAttributes import get_downloadAttributes
# from scripts.artifacts.spotlightSearches import get_spotlightSearches
# from scripts.artifacts.spotlightApplicationUsage import get_spotlightApplicationUsage
# from scripts.artifacts.spotlightLocations import get_spotlightLocations
# from scripts.artifacts.spotlightDownloads import get_spotlightDownloads
# from scripts.artifacts.spotlightSharedFiles import get_spotlightSharedFiles
# from scripts.artifacts.spotlightReceivedFiles import get_spotlightReceivedFiles
# from scripts.artifacts.shellHistory import get_shellHistory
# from scripts.artifacts.shellSessions import get_shellSessions
# from scripts.artifacts.autorunsAgentsApple import get_autorunsAgentsApple
# from scripts.artifacts.autorunsAgentsNonApple import get_autorunsAgentsNonApple
# from scripts.artifacts.autorunsAgentsUser import get_autorunsAgentsUser
# from scripts.artifacts.autorunsDaemonsApple import get_autorunsDaemonsApple
# from scripts.artifacts.autorunsDaemonsNonApple import get_autorunsDaemonsNonApple
# from scripts.artifacts.autorunsLoginItems import get_autorunsLoginItems

from scripts.macCocktail_functions import *

# Fle locations for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'File Location(s) list')
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

#tosearch = {'systemDetails':('1 - System Overview', ['/System/Library/CoreServices/SystemVersion.plist', \
#                '/private/var/folders/zz/zyxvpxvq6csfxvn_n00000sm00006d/C/cache_encryptedA.db', \
#                '/private/var/db/.AppleSetupDone', \
#                '/Library/Preferences/SystemConfiguration/preferences.plist', \
#                '/Library/Preferences/com.apple.loginwindow.plist']),
tosearch = {'systemDetails':('System Overview'),
            'timeZone':('System Overview'),
            'userAccounts':('Accounts'),
            'userAccountsDeleted':('Accounts'),
            'networkInterfaces':('Network'),
            'networkConfiguration':('Network'),
            'networkHistory':('Network')
            }
#             'internetAccounts':('2 - Accounts', ['/Library/Preferences/SystemConfiguration/com.apple.accounts.exists.plist']),
#             'internetAccountsConfiguration':('2 - Accounts', ['/Users/','/Library/Accounts/Accounts4.sqlite']),
#             'iDeviceConnections':('Connections', ['/Users/','/Library/Preferences/com.apple.iPod.plist']),
#             'iDeviceBackups':('Connections', ['NA']),
#             'iDevicelockdownFiles':('Connections', ['/private/var/db/lockdown/']),
#             'officeExcelMRUs':('Recent Activity', ['/Users/','/Library/Containers/com.microsoft.Excel/Data/Library/Preferences/com.microsoft.Excel.securebookmarks.plist']),
#             'officeWordMRUs':('Recent Activity', ['/Users/','/Library/Containers/com.microsoft.Word/Data/Library/Preferences/com.microsoft.Word.securebookmarks.plist']),
#             'officePowerPointMRUs':('Recent Activity', ['/Users/','/Library/Containers/com.microsoft.Powerpoint/Data/Library/Preferences/com.microsoft.Powerpoint.securebookmarks.plist']),
#             'recentFolders':('Recent Activity', ['/Users/','/Library/Preferences/com.apple.finder.plist']),
#             'recentDocuments':('Recent Activity', ['/Users/','/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments']),
#             'shellHistory':('Recent Activity', ['NA']),
#             'shellSessions':('Recent Activity', ['/Users/','/.bash_sessions/']),
#             'downloadAttributes':('Downloads', ['/Users/','/Downloads']),
#             'spotlightSearches':('Spotlight', ['NA']),
#             #'spotlightApplicationUsage':('Spotlight', ['/Applications/']),
#             #'spotlightLocations':('Spotlight', ['NA']),
#             #'spotlightDownloads':('Spotlight', ['NA']),
#             #'spotlightSharedFiles':('Spotlight', ['NA']),
#             #'spotlightReceivedFiles':('Spotlight', ['NA']),
#             'autorunsAgentsApple':('Autoruns', ['NA']),
#             'autorunsAgentsNonApple':('Autoruns', ['NA']),
#             'autorunsAgentsUser':('Autoruns', ['NA']),
#             'autorunsDaemonsApple':('Autoruns', ['NA']),
#             'autorunsDaemonsNonApple':('Autoruns', ['NA']),
#             'autorunsLoginItems':('Autoruns', ['NA'])
#            }


slash = '\\' if is_platform_windows() else '/'

def process_artifact(macos_version, artifact_func, artifact_name, report_folder_base, input_path):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
    '''
    
    logfunc('{} artifact executing'.format(artifact_func))
    artifact_success = 0
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_func))
        logfunc('Error was {}'.format(str(ex)))
        return artifact_success
    try:
        method = globals()['get_' + artifact_func]
        artifact_success = method(macos_version, report_folder, input_path)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_func))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return artifact_success

    if artifact_success != 0:
        logfunc('{} artifact completed'.rstrip().format(artifact_func))
    return artifact_success
