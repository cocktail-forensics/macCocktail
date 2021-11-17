import argparse
import os
import scripts.report as report
import shutil
import sys

from scripts.macCocktail_functions import *
from scripts.macCocktail_artifacts import *
from scripts.version_info import macCocktail_version
from time import process_time, gmtime, strftime

def main():
    parser = argparse.ArgumentParser(description='macCocktail: Gather forensic artifacts from macOS file systems')
    #parser.add_argument('-t', choices=['fs','tar','zip'], required=True, action="store", help="Input type (fs = extracted to file system folder)")
    parser.add_argument('-o', '--output_path', required=True, action="store", help='Output folder path')
    parser.add_argument('-i', '--input_path', required=True, action="store", help='Path to mounted input directory')
        
    args = parser.parse_args()

    input_path = args.input_path
    output_path = os.path.abspath(args.output_path)
    extracttype = 'fs'

    if len(output_path) == 0:
        print('No OUTPUT folder selected. Run the program again.')
        return

    if len(input_path) == 0:
        print('No INPUT folder selected. Run the program again.')
        return

    if not os.path.exists(input_path):
        print('INPUT folder does not exist! Run the program again.')
        return  

    out_params = OutputParameters(output_path)

    crunch_artifacts(extracttype, input_path, out_params)
        
def crunch_artifacts(extracttype, input_path, out_params):
    start = process_time()

    logfunc('\nProcessing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'macCocktail v{macCocktail_version}: Gather forensic artifacts from macOS file systems')
    logfunc('Parsing By: The Bartender | @Cocktail4n6 | cocktailforensics.com')
    logfunc('Framework By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('Framework By: Yogesh Khatri | @SwiftForensics | swiftforensics.com')
    logdevinfo()

    # Now ready to run
    logfunc(f'\nArtifact categories to parse: {str(len(tosearch))}')
    logfunc(f'Mounted directory selected: {input_path}')
    logfunc('--------------------------------------------------------------------------------------\n')

    log = open(os.path.join(out_params.report_folder_base, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Mounted directory selected: {input_path}<br><br>')

    # Clean input directory
    if input_path[-1] == "/":
        input_path = input_path[:-1]
    
    categories_searched = 0
    # Search for the files per the arguments
    for key, val in tosearch.items():
        artifact_pretty_name = val
        macos_version = get_macos_version(input_path)
        logfunc(f'macOS version detected: {macos_version}\n')
        artifact_success = process_artifact(macos_version, key, artifact_pretty_name, out_params.report_folder_base, input_path)

        if artifact_success == 0:
            logfunc(f'***File(s) not found when attempting to parse {key}, artifact unparsed\n')
            log.write(f'File(s) not found for {key} <br><br>')
        else:
            logfunc()
            log.write(f'File(s) for {key} was found.<br><br>')
        categories_searched += 1
        GuiWindow.SetProgressBar(categories_searched)
    log.close()

    logfunc('--------------------------------------------------------------------------------------')
    logfunc('Processes completed.')
    end = process_time()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    report.generate_report(out_params.report_folder_base, run_time_secs, run_time_HMS, extracttype, input_path)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {out_params.report_folder_base}\n')

if __name__ == '__main__':
    main()