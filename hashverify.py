import hashlib
import os
import sys
from datetime import datetime

# Script usage: python /path/to/script /path/to/collection/directory
# Ensure manifest is somewhere in this directory (it can be outside the folder containing the collection contents)

#Select the directory containing the files to be verified
dir_to_verify = sys.argv[1]

# Create dictionary to pair file paths with their original checksums
hash_dict = {}

timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

print(f'Checksum validation results for {dir_to_verify}\nDate/Time: {timestamp}')

for root, dirs, files in os.walk(dir_to_verify):
    count = 0
    for file in files:
        if 'manifest' in str(file).lower(): #Identify the manifest file.
            #manifest_conf = input(f'\nConfirm this is the file manifest: {file}\nType Y or N: ') #Prompt user for input to confirm correct manifest file.
            #if manifest_conf.lower() == 'y': #If user confirms, open and read the file. Parse the tabulated data by column and add filename:checksum pairs to a dictionary.
            if str(file).lower().endswith('.txt'):
                manifest_file = os.path.join(root, file)
                with open(manifest_file, 'r') as manifest:
                    for line in manifest.readlines():
                        cols = line.split('\t')
                        full_filename = cols[0]
                        filename=str(full_filename) #Convert filenames from repr to str for easier matching in the next step.
                        md5 = cols[7]
                        hash_dict[filename] = md5
                        continue

            #If user does not confirm, continue searching.
            #else:
                #print(f'\nContinuing to search for manifest file...')

        #For all other files in the directory, generate MD5 checksums and compare with the saved checksum in the diectionary.
        else:
            count+=1
            filepath = os.path.join(root, file) 
            file_to_check = str(filepath)
            with open(filepath, 'rb') as f: # Open the file in readable binary format so it can be funneled to the hashlib MD5 algorithm   
                data = f.read()
                md5_generated = hashlib.md5(data).hexdigest() # Pipe the binary file data to the checksum generator. Hexdigest returns a typical MD5 string of hexadecimal digits.
                orig_md5 = hash_dict.get(file_to_check, None) #Pair the file path with a file path in the dictory

                if md5_generated == orig_md5: # Compare the new md5 checksum with the original checksum pulled from the dictionary
                    print(f'\n{count}) Checksum VALIDATED: {file_to_check}')

                    #Uncomment print statement below to display all checksum comparisons.
                    #print(f'   >> MD5 in manifest: {orig_md5}\n   >> Current MD5:     {md5_generated}\n\n--------------------------')

                else:
                    print(f'\n{count}) Checksum NOT VALIDATED: {file_to_check}\n   >> MD5 in manifest: {orig_md5}\n   >> Current MD5:     {md5_generated}')

hash_dict.pop('Full Name (Path+File)')
#print(hash_dict)
