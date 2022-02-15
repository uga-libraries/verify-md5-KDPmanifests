import hashlib
import os
import sys
import csv
import datetime

# Script usage: python /path/to/script /path/to/accession/directory
# The manifest needs to be somewhere in this directory (it can be outside the folder containing the collection materials)

# Select the directory containing the files to be verified
dir_to_verify = sys.argv[1]

# Create a dictionary to pair file paths with their original checksums
hash_dict = {}

date = datetime.now().strftime("%Y%m%d")

# Create an empty list to hold the names of invalid files
invalid = []

with open(f'{dir_to_verify}\\validation_log_{date}.csv', "w", newline='') as log_file: # Create a new CSV validation log in the current accession folder
    writer = csv.writer(log_file)
    header = ['Timestamp', 'File', 'Checksum_Validated', 'MD5_in_Manifest', 'Current_MD5']
    writer.writerow(header)
    for root, dirs, files in os.walk(dir_to_verify): # Walk through the accession folder
        for file in files:
            if 'manifest' in str(file).lower(): #Identify the manifest file
                if str(file).lower().endswith('.txt'):
                    manifest_file = os.path.join(root, file)
                    with open(manifest_file, 'r') as manifest: # Open the manifest and read the tabulated data by column 
                        for line in manifest.readlines():
                            cols = line.split('\t')
                            full_filename = cols[0]
                            filename=str(full_filename) #Convert filenames from repr to str for easier matching in the next step
                            md5 = cols[7]
                            hash_dict[filename] = md5 # Add filename:checksum pairs to a dictionary
                            continue

            #Skip over the validation log once it's created
            elif 'validation_log' in str(file).lower():
                continue

            #For all other files in the directory, generate MD5 checksums and compare with the saved checksum in the dictionary.
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                filepath = os.path.join(root, file) 
                file_to_check = str(filepath)
                with open(filepath, 'rb') as f: # Open the file in readable binary format so it can be funneled to the hashlib MD5 algorithm   
                    data = f.read()
                    md5_generated = hashlib.md5(data).hexdigest() # Pipe the binary file data to the checksum generator, "hexdigest" returns a typical MD5 string of hexadecimal digits
                   
                    orig_md5 = hash_dict.get(file_to_check, None) # Get the original checksum from the dictionary

                    if md5_generated == orig_md5: # If the new MD5 exactly matches the MD5 from the manifest, write the validation results to the log
                        data = [timestamp, file_to_check, "TRUE"]
                        writer.writerow(data)

                    else: # If they don't match, write the validation results to the log and print an error message to the terminal
                        data = [timestamp, file_to_check, "FALSE", orig_md5, md5_generated]
                        writer.writerow(data)
                        print(f"\nInvalid checksum for {file}. See validation log.")
                        invalid.append(file_to_check) # Add the file name to the list
 
#hash_dict.pop('Full Name (Path+File)')

if not invalid: #If there is nothing in the error list, this will return "FALSE" and a "No errors" message will display in the terminal
    print("\nAll files have been validated. There are no errors.")

print(f'\nSee validation log in accession folder.') # Indicates that the script is done and reminds the user where the log has been stored
