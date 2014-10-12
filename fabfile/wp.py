import logging

from fabric.api import task, sudo, put, cd, execute, settings, env
from fabric.contrib.files import sed

from conf.conf import *

@task
# must escape certain characters in passwords with two backslashes: &, $ (or avoid them!)
def new():
    '''Downloads and installs Wordpress.
    '''

    sudo('mkdir -p ' + WP_HOME, warn_only=True)
    sudo('chown -R ' + USER_NAME + ':' + USER_NAME + ' ' + WP_HOME)

    # get wordpress source
    with cd('/usr/local/src'):
        sudo('wget http://wordpress.org/latest.tar.gz')
        sudo('tar -xzvf latest.tar.gz')
        sudo('mv wordpress/* ' + WP_HOME)

    execute(config)
    # also need to change AllowOverride None to AllowOverride All in <Directory "/var/www/html"> section of httpd.conf (or wherever WP is served from)

@task
def config():
    '''Configures Wordpress installation.
    '''

    load_secrets()

    # create /tmp/wp_config by deleting default lines for auth keys and such that we don't need
    CONFIG_SAMPLE = WP_HOME + '/wp-config-sample.php'
    CONFIG = WP_HOME + '/wp-config.php'
    sudo('grep -vwE "(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|AUTH_SALT|SECURE_AUTH_SALT|LOGGED_IN_SALT|NONCE_SALT)" ' + CONFIG_SAMPLE + ' > /tmp/wp_config')

    # get random secret keys from wordpress, add them to /tmp/wp_config, and copy them to CONFIG
    sudo('wget https://api.wordpress.org/secret-key/1.1/salt/ -O /tmp/wp_secrets')
    with cd('/tmp'):
        sudo(r'csplit -f wp_ wp_config "/\*\*#@-\*/"')
        sudo('cat wp_00 wp_secrets wp_01  >> ' + CONFIG)
        sudo('rm wp_*')

    # replace database credentials
    sed(WP_HOME + '/wp-config.php', 'database_name_here', env.SECRETS['wp_db_name'], use_sudo=True)
    sed(WP_HOME + '/wp-config.php', 'username_here', env.SECRETS['wp_db_user'], use_sudo=True)
    sed(WP_HOME + '/wp-config.php', 'password_here', env.SECRETS['wp_db_user_password'], use_sudo=True)
    sed(WP_HOME + '/wp-config.php', 'localhost', env.SECRETS['wp_db_host'], use_sudo=True)
    sed(WP_HOME + '/wp-config.php', 'wp_', env.SECRETS['wp_db_name'] + '_', use_sudo=True)

    # clean up after sed
    sudo('rm ' + WP_HOME + '/wp-config.php.bak')

    # set file permissions and ownership
    with cd(WP_HOME):
        sudo('touch .htaccess')
        sudo('chown ' + USER_NAME + ':' + USER_NAME + ' .htaccess')
        sudo('chmod 666 .htaccess')