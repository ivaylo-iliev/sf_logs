import os.path
import json
import argparse

if not os.path.isdir(os.path.join('.', 'profiles')):
    os.makedirs(os.path.join('.', 'profiles'))

parser = argparse.ArgumentParser(description='Usage:')
requiredNamed = parser.add_argument_group('Required arguments')
requiredNamed.add_argument('-n', '--name', type=str, help='Profile name')
requiredNamed.add_argument('-u', '--user', type=str, help='User name')
requiredNamed.add_argument('-p', '--password', type=str, help='Password')
requiredNamed.add_argument('-s', '--security_token', type=str, help='Security token')
requiredNamed.add_argument('-t', '--type', type=int, help='Environment type. 0 = Sandbox, 1 = Production')
requiredNamed.add_argument('-i', '--instance_url', type=str, help='Instance URL')

args = parser.parse_args()

if (args.name is None) or (args.user is None) or (args.password is None) or (args.security_token is None):
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

file_name = os.path.join('.', 'profiles', args.name + '.json')

if os.path.isfile(file_name):
    ans = input('Profile "{name}" already exists. Do you which to replace it? [Y/N] : '.format(name=args.name))
    if (ans is 'Y') or (ans is 'y'):
        print('Replacing profile {name}'.format(name=args.name))
        os.remove(file_name)
    else:
        exit(0)
else:
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

