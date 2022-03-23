import hashlib
import os
import sys
import csv
from datetime import datetime

# This script parses hash logs generated by hashverify_withlog.py
# It validates file fixity by generating a new MD5 checksum and comparing it to the MD5 in the log.
# It also skips over common preservation documentation like Duke Data Accessioner logs and media inventories.

# Script usage: python /path/to/script /path/to/accession/directory
# The log generated by hashverify_withlog.py needs to be somewhere in the specified accession directory and named with the "validation_log_{date}.csv" format generated by the script.

# Select the directory containing the files to be verified
dir_to_verify = sys.argv[1]

# Create a dictionary to pair file paths with their saved checksums in the log
hash_dict = {}

date = datetime.now().strftime("%Y%m%d")

# An empty list to hold the names of invalid files
invalid = []

# An empty list to hold the names of all files in the current directory
files_in_dir = []

count = 0
print(f'\nAll validation results will be saved to the log file.')

with open(f'{dir_to_verify}\\post-migration_validation_log_{date}.csv', "w", newline='') as log_file: # Create a new CSV validation log in the current accession folder
    writer = csv.writer(log_file)
    header = ['Timestamp', 'File', 'ChecksumValidated', 'MD5inValidationLog', 'CurrentMD5', 'ErrorMessage', 'Notes']
    writer.writerow(header)
    for root, dirs, files in os.walk(dir_to_verify): # Walk through the accession folder
        for file in files:
            fname = str(file).lower()
            to_skip = ['data-accessioner','dataaccessioner', 'manifest.txt', 'media-inventory','normalized-filenames','post-migration', 'preservation.txt','preservation-log','preservation_log','PreservationLog','preservationlog']
            if any(x in fname for x in to_skip): # Skip over as much preservation documentation as possible
                continue
            elif (fname.startswith('validation_log')) and (fname.endswith('.csv')): # Identify the log file with two conditions
                log_file = os.path.join(root, file)
                with open(log_file, 'r') as log: # Open the log file
                    reader = csv.reader(log, delimiter=',')
                    next(reader, None) # Skip the header row
                    for row in reader: # Iterate over the log and parse out file name and MD5 data
                        full_filename = row[1]
                        file_str = str(full_filename) # Convert filenames from repr to str for easier matching in the next step
                        filename = file_str.replace('"', '') # Remove random quotations that are around some of the file paths
                        if row[4]: # Avoid errors where MD5 data is missing
                            md5 = row[4]
                        else:
                            md5 = None
                        hash_dict[filename] = md5 # Add filename:checksum pairs to a dictionary
                        continue

            else: # Iterate through the other files in the directory, generate their MD5 checksums and compare them with the saved checksums in the dictionary  
                timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                filepath = os.path.join(root, file) 
                file_to_check = str(filepath)
                files_in_dir.append(file_to_check) # Add it to the running list of all files in the directory
                if len(file_to_check) > 250:
                    file_to_check = (f'\\\\?\\{file_to_check}')  # Adds extended-length path prefix to prevent Windows OSErrors from file paths longer than 260 chars
                with open(filepath, 'rb') as f: # Open the file in readable binary format so it can be funneled to the hashlib MD5 algorithm   
                    data = f.read()
                    md5 = hashlib.md5(data).hexdigest() # Pipe the binary file data to the checksum generator, "hexdigest" returns a typical MD5 string of hexadecimal digits
                    md5_generated = md5.upper() # Format it to match the MD5 in the log
                    if file_to_check.startswith('\\\\?\\'): # Removes extended-length path prefix for matching purposes
                        file_to_check = str(file_to_check[4:])
                    orig_md5 = hash_dict.get(file_to_check, None) # Get the original checksum from the dictionary
                    if md5_generated == orig_md5: # Check if the new MD5 exactly matches the MD5 from the log
                        data = [timestamp, file_to_check, "TRUE", orig_md5, md5_generated] # Add it to the new log
                        writer.writerow(data)
                    else:
                        if orig_md5 == None: # Indicates that the file is missing from the old log altogether
                            data = [timestamp, file_to_check, "FALSE", None, md5_generated, "Missing from log"] # Add it to the new log
                            writer.writerow(data)
                            count+=1 
                            print(f'\n\t{count}) IN DIRECTORY BUT MISSING FROM LOG: {file_to_check}')

                        else: # This means the checksums don't match
                            data = [timestamp, file_to_check, "FALSE", orig_md5, md5_generated, "Checksums do not match"] # Add it to the new log
                            writer.writerow(data)
                            count+=1 
                            print(f'\n\t{count}) INVALID CHECKSUM: {file_to_check}')
                        invalid.append(file_to_check) # Add the file name to the list of invalid files

    for key in hash_dict: # Iterate thru the dict containing the log files and compare it to the list containing the directory files
        if key in files_in_dir: # If the file is in both, do nothing
            continue
        else: # This means there's a mismatch between the lists
            count+=1
            orig_md5 = hash_dict.get(key, 'NO MD5 FOUND IN LOG') # Get the MD5 from the old log
            data = [timestamp, key, "FALSE", orig_md5, None, f'Missing from specified directory: {dir_to_verify}'] # Add it to the new log
            writer.writerow(data)
            print(f'\n\t{count}) IN LOG BUT MISSING FROM DIRECTORY: {key}')

if not invalid: #If there is nothing in the error list, this will return "FALSE" and a "No errors" message will display in the terminal
    print('\nALL FILES HAVE BEEN VALIDATED. THERE ARE NO ERRORS.')

print(f'\nScript is finished. See validation log in accession folder.') # Indicates that the script is done and reminds the user where the new log has been stored
