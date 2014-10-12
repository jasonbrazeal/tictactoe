import logging

from fabric.api import task, sudo, env, local, run, put, cd, execute, settings
from fabric.contrib.files import sed

from conf.conf import *

@task
def initialize():
    '''Initializes a git repo and connects it to REPO_URL. Assumes repo has been initialized with README.md at REPO_URL.
    '''
    with cd(PROJECT_DIR):
        run('git init')
        sudo('git remote add origin ' + REPO_URL)
        sudo('git pull origin master')

def configure_git_globals():
    sudo('git config --global user.name "' + DEVELOPER_NAME + '"')
    sudo('git config --global user.email ' + DEVELOPER_EMAIL)
    # sudo('git config --global push.default simple')