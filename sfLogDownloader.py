import os.path
import json
import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor
from simple_salesforce import Salesforce, exceptions


def download_log(instance, log_url, log_id, headers):
    try:
        logUrl = '{instance}{log}/Body'.format(instance=instance, log=log_url)
        req_result = sf.request.get(logUrl, headers=headers)
        log_file_name = os.path.join(output_dir, log_id + '.log')
        with open(log_file_name, mode='w') as log_file:
            log_file.write(req_result.text)
        log_file.close()
        print('Done with log ' + log_id)
    except Exception as e:
        print(traceback.format_exc())


if not os.path.isdir(os.path.join('.', 'profiles')):
    print('No connection profiles defined. Please use the addConfiguration.py script to create one.')
    exit(1)

parser = argparse.ArgumentParser(description='Usage:')
parser.add_argument('-o', '--output_dir', type=str, help='Output directory')
requiredNamed = parser.add_argument_group('Required arguments')
requiredNamed.add_argument('name', help='Profile name')

args = parser.parse_args()

file_name = os.path.join('.', 'profiles', args.name + '.json')

if not os.path.isfile(file_name):
    print('No profile with name "{name}" exists.'.format(name=args.name))
    print('Please use the addConfiguration.py script to create it.')
    exit(0)

username = None
password = None
security_token = None
domain = None
instance_url = None
output_dir = None

with open(file_name) as json_file:
    data = json.load(json_file)
    for value in data['profile']:
        username = value['user']
        password = value['password']
        security_token = value['token']
        instance_url = value['instance-url']

        if value['type'] is 0:
            domain = 'test'
        else:
            domain = 'login'

sf = None

try:
    sf = Salesforce(username=username, password=password, security_token=security_token, domain=domain, version="46.0")
except exceptions.SalesforceAuthenticationFailed:
    print('Invalid username, password, security token; or user locked out.')
    exit(1)

if args.output_dir is not None:
    output_dir = args.output_dir
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
else:
    output_dir = './output/{name}'.format(name=args.name)
    if not os.path.isdir('./output/{name}'.format(name=args.name)):
        os.makedirs('./output/{name}'.format(name=args.name))

log_data = sf.query_all(
    'Select Id, LogUserId, LogLength, LastModifiedDate, Request, Operation, Application, Status, DurationMilliseconds, SystemModstamp, StartTime, Location FROM ApexLog')

items = list(log_data['records'])

if len(items) == 0:
    print("No logs to download found. Exiting.")
    exit(2)
else:
    with ThreadPoolExecutor(max_workers=100) as executor:
        for item in items:
            future = executor.submit(download_log, instance_url, item['attributes']['url'], item['Id'], sf.headers)
