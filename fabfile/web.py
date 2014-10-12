from fabric.api import task, sudo, env, local, put, cd, execute
from fabric.contrib.files import sed, append

import os

from conf.conf import *

@task
def provision_apache(dev=False, vhost=False):
    install_package('httpd')
    # disable welcome page
    sudo('mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.off')
    # configure apache
    local("sed -e 's/<SERVER_NAME>/" + env.hostname + "/g' -e 's/<SERVER_ADMIN>/" + SERVER_EMAIL + "/g' conf/web/template.vm_centos.httpd.conf > conf/web/httpd.conf")
    put('conf/web/httpd.conf', '/etc/httpd/conf/httpd.conf', use_sudo=True)
    local('rm conf/web/httpd.conf')
    if vhost:
        execute(add_vhost)
    if dev:
        put('conf/web/template.vm_centos.dev.conf', '/etc/httpd/conf.d/dev.conf', use_sudo=True)
    execute(restart_apache)

@task
def add_vhost():
    VHOST = '''
<VirtualHost *:80>
    DocumentRoot {0}
    ServerName {1}
    ErrorLog logs/error_log-{1}
    CustomLog logs/access_log-{1} common
    CheckSpelling On
    Options -Indexes
</VirtualHost>'''.format(APACHE_DOCROOT, PROJECT_NAME)
    append('/etc/httpd/conf.d/vhost.conf', VHOST, use_sudo=True)

@task
def add_wsgi_vhost():
    sudo('useradd {0}'.format(PROJECT_NAME))
    VHOST = '''
<VirtualHost *:80>
    DocumentRoot {0}
    ServerName {1}
    ErrorLog logs/error_log-{1}
    CustomLog logs/access_log-{1} common
    WSGIDaemonProcess {1} user={1} group={1} threads=5
    WSGIScriptAlias / {2}/{1}.wsgi

    <Directory {2}>
        WSGIProcessGroup {1}
        WSGIApplicationGroup %{{GLOBAL}}
        Order deny,allow
        Allow from all
    </Directory>

</VirtualHost>'''.format(APACHE_DOCROOT, PROJECT_NAME, WSGI_PATH)
    append('/etc/httpd/conf.d/wsgi.conf', VHOST, use_sudo=True)

@task
def provision_wsgi():
    '''The easier version, 'yum -y install mod_wsgi', did not work on CentOS 6.5. At least I couldn't find a way to tell it not to use the system Python.
    '''
    install_package('httpd-devel')
    with cd('/usr/local/src'):
        sudo('wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.3.0.tar.gz')
        sudo ('tar xzvf 4.3.0.tar.gz')
        with cd('mod_wsgi-4.3.0'):
            sudo('./configure  --with-python=/usr/local/bin/python2.7')
            sudo('make')
            sudo('make install')

@task
def provision_php():
    for p in ['php', 'php-mysql', 'php-xml']:
        install_package(p)
    # configure php
    # set time zone in php.ini
    sed('/etc/php.ini', ';date.timezone =', 'date.timezone = "America/New_York"', use_sudo=True)
    # don't show version
    sed('/etc/php.ini','expose_php = On','expose_php = Off', use_sudo=True)
    execute(restart_apache)

@task
def test_php():
    sudo('echo "<?php phpinfo(); ?>" >> /tmp/test.php', shell=False)
    sudo('mv /tmp/test.php ' + APACHE_DOCROOT, shell=False)

@task
def test_html():
    sudo('echo "<h1>* hello :)<h1>" >> /tmp/test.html', shell=False)
    sudo('mv /tmp/test.html ' + APACHE_DOCROOT, shell=False)

@task
def restart_apache():
    sudo('/sbin/chkconfig httpd on', shell=False)
    sudo('/sbin/service httpd restart', shell=False)

@task
def start_apache():
    sudo('/sbin/chkconfig httpd on', shell=False)
    sudo('/sbin/service httpd start', shell=False)

@task
def stop_apache():
    sudo('/sbin/service httpd stop', shell=False)

@task
def reset_httpd_conf():
    put('conf/web/default_centos.httpd.conf', '/etc/httpd/conf/httpd.conf', use_sudo=True)