import os.path
import json
import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor
from simple_salesforce import Salesforce, exceptions
from getpass import getpass
import pyAesCrypt
from tqdm import tqdm
from sys import argv
from os import walk
from pathlib import Path

profile_settings = None
progress_bar = None
sf = None

home_directory = str(Path.home())


def download_log(log_id, headers):
    try:
        log_location = '{base_url}sobjects/ApexLog/{log}/Body'.format(base_url=sf.base_url, log=log_id)
        print(log_location)
        #req_result = sf.request.get(log_location, headers=headers)
        req_result = sf.session.get(log_location, headers=headers)
        log_file_name = os.path.join(output_dir, log_id + '.log')
        with open(log_file_name, mode='w', encoding='utf8') as log_file:
            log_file.write(req_result.text)
        log_file.close()
        progress_bar.update(1)
    except Exception:
        print(traceback.format_exc())


def decrypt_profile(file):
    data = None
    if os.path.isfile(file):
        buffer_size = 64 * 1024
        enc_password = getpass('Please enter encryption password:')
        try:
            pyAesCrypt.decryptFile(file, file[:-4], enc_password, buffer_size)
            with open(file[:-4]) as json_file:
                data = json.load(json_file)
            os.remove(file[:-4])
        except ValueError:
            print('Wrong password (or file is corrupted)!')
            exit(2)
    return data


def read_settings(file):
    settings = None
    if ".aes" in file:
        settings = decrypt_profile(file)
    else:
        with open(file) as json_file:
            settings = json.load(json_file)
    return settings


if not os.path.isdir(os.path.join(home_directory, '.sf_tools', 'profiles')):
    print('No connection profiles defined. Please use the addConfiguration.py script to create one.')
    exit(1)

parser = argparse.ArgumentParser(description='Usage:')
parser.add_argument('-o', '--output_dir', type=str, help='Output directory')
requiredNamed = parser.add_argument_group('Required arguments')
requiredNamed.add_argument('name', help='Profile name')

if not len(argv) > 1:
    if os.path.isdir(os.path.join(home_directory, '.sf_tools', 'profiles')):
        files = []
        for (_, _, filenames) in walk(os.path.join(home_directory, '.sf_tools', 'profiles')):
            files.extend(filenames)
        if len(files) > 0:
            print('No profile specified. Please one one of the following:\n')
            for file in files:
                if '.aes' in file:
                    print(file[:-9])
                else:
                    print(file[:-5])
        else:
            print('No connection profiles defined. Please use the addConfiguration.py script to create one.')
    exit(0)

args = parser.parse_args()

file_name = os.path.join(home_directory, '.sf_tools', 'profiles', args.name + '.json')
enc_file_name = file_name + '.aes'
file_is_encrypted = False

if not os.path.isfile(file_name) and not os.path.isfile(enc_file_name):
    print('No profile with name "{name}" exists.'.format(name=args.name))
    print('Please use the addConfiguration.py script to create it.')
    exit(0)

if os.path.isfile(enc_file_name):
    profile_settings = read_settings(enc_file_name)
elif os.path.isfile(file_name):
    profile_settings = read_settings(file_name)

username = None
password = None
security_token = None
domain = None
output_dir = None

for value in profile_settings['profile']:
    username = value['user']
    password = value['password']
    security_token = value['token']

    if value['type'] == 0:
        domain = 'test'
    else:
        domain = 'login'

sf = None

try:
    sf = Salesforce(username=username, password=password, security_token=security_token, domain=domain, version="46.0")
except exceptions.SalesforceAuthenticationFailed:
    print('Invalid username, password, security token; or user locked out.')
    exit(1)

if args.output_dir != None:
    output_dir = args.output_dir
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
else:
    output_dir = './output/{name}'.format(name=args.name)
    if not os.path.isdir('./output/{name}'.format(name=args.name)):
        os.makedirs('./output/{name}'.format(name=args.name))

log_data = sf.query_all(
    'Select '
    '   Id, '
    '   LogUserId, '
    '   LogLength, '
    '   LastModifiedDate, '
    '   Request, '
    '   Operation, '
    '   Application, '
    '   Status, '
    '   DurationMilliseconds, '
    '   SystemModstamp, '
    '   StartTime, '
    '   Location '
    'FROM ApexLog')

items = list(log_data['records'])

if len(items) == 0:
    print("No logs to download found. Exiting.")
    exit(1)
else:
    progress_bar = tqdm(total=len(items), unit='B')
    with ThreadPoolExecutor(max_workers=100) as executor:
        for item in items:
            future = executor.submit(download_log, item['Id'], sf.headers)
    progress_bar.close()