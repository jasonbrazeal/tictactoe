import logging

from fabric.api import task, sudo, env, settings
from fabric.contrib.files import sed
from fabric.operations import get, put

from conf.conf import *

@task
def setup():
    '''Installs MySQL database.
    '''
    load_secrets()
    install_package('mysql-server')
    # The prompts dictionary is supported beginning in Fabric 1.8.1
    # Run `pip install https://github.com/fabric/fabric/zipball/master` to pull down the latest version
    # The function works fine with earlier version, but you have to respond to the prompts manually
    with settings(prompts = {
                             'Enter current password for root (enter for none): ': '',
                             'Set root password? [Y/n] ': 'Y',
                             'New password: ': env.SECRETS['mysql_root_password'],
                             'Re-enter new password: ': env.SECRETS['mysql_root_password'],
                             'Remove anonymous users? [Y/n] ': 'Y',
                             'Disallow root login remotely? [Y/n] ': 'Y',
                             'Remove test database and access to it? [Y/n] ': 'Y',
                             'Reload privilege tables now? [Y/n] ': 'Y'
                             }):
        sudo('/sbin/service mysqld start')
        sudo('/usr/bin/mysql_secure_installation')
    sed('/etc/my.cnf', '\[mysqld\]', '\[mysqld\]\\nbind-address=127.0.0.1', use_sudo=True)
    sudo('/sbin/chkconfig mysqld on')
    sudo('/sbin/service mysqld start')

@task
def create(type):
    '''Puts the init.sql script on the server and runs it as root to create a new database. Type should match the prefix in secrets.json (e.g. "dj", "wp", etc.).
    '''
    load_secrets()
    put('conf/db/init.sql', '/tmp/init.sql', use_sudo=True)

    # replace database credentials in init.sql
    sed('/tmp/init.sql', '<DB_NAME>', env.SECRETS[type + '_db_name'], use_sudo=True)
    sed('/tmp/init.sql', '<DB_USER>', env.SECRETS[type + '_db_user'], use_sudo=True)
    sed('/tmp/init.sql', '<DB_PASSWORD>', env.SECRETS[type + '_db_user_password'], use_sudo=True)
    sed('/tmp/init.sql', '<DB_HOST>', env.SECRETS[type + '_db_host'], use_sudo=True)

    # run init.sql script
    with settings(prompts = {
                             'Enter password: ': env.SECRETS['mysql_root_password']
                             }):
        sudo('/usr/bin/mysql -vvv --show-warnings -h ' + env.SECRETS[type + '_db_host'] + ' -u root -p < /tmp/init.sql')
    sudo('rm /tmp/init.sql /tmp/init.sql.bak')

@task
def backup(db_name, backup_location='/Users/jsonbrazeal/Desktop'):
    load_secrets()
    with settings(prompts = {
                             'Enter password: ': env.SECRETS['mysql_root_password']
                             }):
        sudo('mysqldump --add-drop-table -h localhost -u root -p ' + db_name + ' > /tmp/' + db_name + '.sql')
    get('/tmp/' + db_name + '.sql', backup_location)
    sudo('rm /tmp/' + db_name + '.sql')

@task
def restore(type, dump_file):
    '''Puts the script given on the server and runs it as root to restore a database. Type should match the prefix in secrets.json (e.g. "dj", "wp", etc.).
    '''
    load_secrets()
    put(dump_file, '/tmp/restore.sql', use_sudo=True)

    # run script from mysqldump
    with settings(prompts = {
                             'Enter password: ': env.SECRETS['mysql_root_password']
                             }):
        sudo('/usr/bin/mysql -vvv --show-warnings -h ' + env.SECRETS[type + '_db_host'] + ' -u root -p ' + env.SECRETS[type + '_db_name'] + ' < /tmp/restore.sql')
    sudo('rm /tmp/restore.sql')

@task
def restart():
    sudo('/sbin/chkconfig mysqld on', shell=False)
    sudo('/sbin/service mysqld restart', shell=False)

@task
def start():
    sudo('/sbin/chkconfig mysqld on', shell=False)
    sudo('/sbin/service mysqld start', shell=False)

@task
def stop():
    sudo('/sbin/service mysqld stop', shell=False)