import os.path
import json
import argparse
from getpass import getpass
import pyAesCrypt
from sys import argv
from pathlib import Path

home_directory = str(Path.home())

if not os.path.isdir(os.path.join(home_directory, '.sf_tools')):
    os.makedirs(os.path.join(home_directory, '.sf_tools'))

if not os.path.isdir(os.path.join(home_directory, '.sf_tools', 'profiles')):
    os.makedirs(os.path.join(home_directory, '.sf_tools', 'profiles'))

parser = argparse.ArgumentParser(description='Usage:')
parser.add_argument('-e', '--encryption-password', type=str, help='Password used to encrypt the profile information')
requiredNamed = parser.add_argument_group('Required arguments')
requiredNamed.add_argument('-n', '--name', type=str, help='Profile name')
requiredNamed.add_argument('-u', '--user', type=str, help='User name')
requiredNamed.add_argument('-p', '--password', type=str, help='Password')
requiredNamed.add_argument('-s', '--security_token', type=str, help='Security token')
requiredNamed.add_argument('-t', '--type', type=int, help='Environment type. 0 = Sandbox, 1 = Production')
requiredNamed.add_argument('-i', '--instance_url', type=str, help='Url of the instance as shown in the web browser for salesforce classic after you login')

args = parser.parse_args()

if not len(argv) > 1:
    parser.print_help()
    exit(0)

if (args.name is None) or (args.user is None) or (args.password is None) or (args.security_token is None) or (args.instance_url is None):
    print('One or more required arguments not provided. Exiting.')
    exit(1)

data = {'profile': []}
data['profile'].append({
    'user': args.user,
    'password': args.password,
    'token': args.security_token,
    'type': args.type,
    'instance-url': args.instance_url
})

file_name = os.path.join(home_directory, '.sf_tools', 'profiles', args.name + '.json')
enc_file_name = file_name + '.aes'

if os.path.isfile(file_name) or os.path.isfile(enc_file_name):
    ans = input('Profile "{name}" already exists. Do you which to replace it? [Y/N] : '.format(name=args.name))
    if (ans is 'Y') or (ans is 'y'):
        print('Replacing profile {name}'.format(name=args.name))

        if os.path.isfile(file_name):
            os.remove(file_name)

        if os.path.isfile(enc_file_name):
            os.remove(enc_file_name)

        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)
    else:
        exit(0)
else:
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)


def encrypt_file(file, passwd):
    if os.path.isfile(file_name):
        buffer_size = 64 * 1024
        pyAesCrypt.encryptFile(file, enc_file_name, passwd, buffer_size)
        os.remove(file_name)


if args.encryption_password is not None:
    encrypt_file(file_name, args.encryption_password)
else:
    ans = input('Do you want to encrypt the profile information? [Y/N]: ')
    if (ans is 'Y') or (ans is 'y'):
        password = getpass("Password: ")
        encrypt_file(file_name, password)
    else:
        print('The profile information will be stored in unsecured plain-text file.')
