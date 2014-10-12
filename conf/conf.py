import logging
import sys
import json
from functools import wraps

from fabric.api import sudo, local, task, env

############################# Project Constants #############################

DEVELOPER_NAME = 'Jason Brazeal'
DEVELOPER_EMAIL = 'jsonbrazeal@gmail.com'
SERVER_EMAIL = 'jasonbrazeal.com@gmail.com'

PROJECT_NAME = 'tictactoe'
PROJECTS_HOME = '/opt'
PROJECT_DIR = PROJECTS_HOME + '/' + PROJECT_NAME

# APACHE_DOCROOT = PROJECT_DIR + '/web'
APACHE_DOCROOT = '/var/www/html'
WP_HOME = PROJECT_DIR + '/blog'
WSGI_PATH = '/var/www/{}'.format(PROJECT_NAME)

SECRETS_DMG = '/Users/jsonbrazeal/Dropbox/Credentials/secrets.dmg'

REPO_NAME = 'tictactoe' # assumes you've already created a github repo with this name
# REPO_URL = 'git@github.com:jsonbrazeal/tictactoe.git'
REPO_URL = 'https://github.com/jsonbrazeal/tictactoe.git'

SERVER_IP_DEV = '104.131.74.88'
HOSTNAME_DEV = 'dev.jasonbrazeal.com'

SERVER_IP_PROD = '107.170.246.58'
HOSTNAME_PROD = 'web1.jasonbrazeal.com'  # 'tictactoe.jasonbrazeal.com'

USER_NAME = 'jsonbrazeal'
SSH_PORT = '4217'
SSH_KEY_FILE = '/Users/jsonbrazeal/.ssh/id_rsa.pub'

PYTHON_VERSION = '2.7.8'
# PYTHON_VERSION = '3.4.1'
# PYTHON_VERSION = None

############################## Helper Functions ##############################

# use this locally; use fabric's sed command to run sed remotely
@task
def replace_in_file(file_name, old, new):
    sudo('sed -i \'s/' + sed_escape(old) + '/' + sed_escape(new)+ ' /g\' ' + file_name, shell=False)

def sed_escape(str):
    return str.replace('/', '\\/').replace('\'', '\'"\'"\'')

@task
def install_package(name, option=''):
    sudo('yum -y ' + option + ' install ' + name, shell=False)

def load_secrets():
    try:
        local('hdiutil attach -stdinpass -mountpoint "$PWD/secrets" ' + SECRETS_DMG)
        with open('secrets/secrets.json') as file:
            json_to_dict = json.load(file)
            # debug:
            # print('json_to_dict = ' + str(json_to_dict))
            # print('json_to_dict[PROJECT_NAME] =' + str(json_to_dict[PROJECT_NAME]))
            env.SECRETS = json_to_dict[PROJECT_NAME]
            # print('env.SECRETS = ' + str(env.SECRETS))
    except:
        sys.exit('Could not open ' + SECRETS_DMG + ' Unexpected error: ' + str(sys.exc_info()[0]))
    try:
        local('hdiutil detach "$PWD/secrets"')
    except:
        sys.exit('Could not close ' + SECRETS_DMG)

@task
def new_encrypted_dmg(name, src_folder=''):
    try:
        local('hdiutil create ' + name + '.dmg -encryption -stdinpass -size 5m -fs JHFS+ -volname ' + name)
    except:
        sys.exit('Error creating  ' + name + '.dmg')
