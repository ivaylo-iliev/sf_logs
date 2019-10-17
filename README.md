# SF_LOGS
#### A tool to easily download Salesforce APEX logs in bulk

## Prerequisites
This script needs to have the following installed on your system:
* Python3
* Pip for python3
* pipenv

## Installation
Clone the repo in a directory of your choosing and execute pipenv install to install all dependencies

```
git clone git@github.com:ivaylo-iliev/sf_logs.git
cd sf_logs
pipenv install
```

## Usage
To access the project's virtual environment use pipenv:
```
pipenv shell
```
### Adding a profile
To add a connection profile use the addConfiguration.py script as shown below:
```
python addConfiguration.py <options>
```
Running the script without any parameters will print a help message. Here is an example of how to use it:
```
python addConfiguration.py -n <ProfileName> -u <Salesforce user> -p <Salesforce password> -s <Salesforce security token> -t <0 or 1> -i <Instance url>
```
```
-n, --name                : Used to specify the name of the connection profile
-u, --user                : Salesforce user to authenticate against an ORG
-p, --password            : Password of the specified Salesforce user
-s, --security_token      : Salesforce security token for the specified user
-t, --type                : Type of the environment. Use 0 for sandbox and 1 for produciton ORG
```
Optionally you can specify an encryption password by using:
```
-e, --encryption-password : Password used to encrypt profile information 
```
Should you decide to specify an encryption password you should remember it since there is no way to recover it and you will not be able to use the profile. If you do not specify an encryption password you will be asked if you want to use one during the script execution. If you do not wish to encrypt the connection profile data choose 'N' when asked.

### Downloading logs from an ORG
To download logs assuming you have created a connection profile all you need to do is to execute the sfLogDownloader.py script inside the pipenv shell:
```
python sfLogDownloader <Connection profile>
```
Optionally you could specify where the logs will be stored by using the -o switch:
```
-o, --output_dir          : Specify a directory where the logs will be stored.
```
If you do not specify an output directory the script will create a output subdirectory in the directory it resides. The logs will be stored in a subdirectory inside it with name the same as the profile name. For example `output/SomeOrgName`. If you have specified encryption password during the profile creation the script will ask for it at runtime.
 
