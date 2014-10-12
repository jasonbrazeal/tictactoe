import logging
import sys

from fabric.api import task, sudo, env, local, run, put,cd, prefix, hosts, lcd, execute, settings
from fabric.contrib.files import sed

from fabtools.vagrant import vagrant # allows us to use any of these tasks on a vagrant vm with the command fab vagrant task_name

from conf.conf import *

############################## Fabfile Imports ##############################

import vm, git, web, dj, wp, db.mysql

############################# Environment Setters #############################

@task
def dev():
    '''Run the following tasks on a development machine.
    '''
    env.user = USER_NAME
    env.hosts = [SERVER_IP_DEV + ':' + SSH_PORT]
    env.hostname = HOSTNAME_DEV

@task
def dev_setup():
    '''Used during initial provisioning (standard SSH port must be used).
    '''
    env.user = 'root'
    env.hosts = [SERVER_IP_DEV]
    env.hostname = HOSTNAME_DEV

@task
def prod():
    '''Run the following tasks on a production machine.
    '''
    env.user = USER_NAME
    env.hosts = [SERVER_IP_PROD + ':' + SSH_PORT]
    env.hostname = HOSTNAME_PROD

@task
def prod_setup():
    '''Used during initial provisioning (standard SSH port must be used).
    '''
    env.user = 'root'
    env.hosts = [SERVER_IP_PROD]
    env.hostname = HOSTNAME_PROD