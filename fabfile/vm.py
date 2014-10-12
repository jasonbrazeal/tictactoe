import logging

from fabric.api import task, sudo, env, local, run, put, cd, execute, settings
from fabric.contrib.files import sed, append

from git import configure_git_globals
from conf.conf import *

@task
def provision_do():
    '''Assumes a clean CentOS install on a Digital Ocean VM. This task is ran at root and connects through the standard SSH port. During this task, the default SSH port is changed and a new user created. This task should be run with the "dev_setup" or "prod_setup" environment setters.'''

    # load credentials, etc. from encrypted SECRETS_DMG specified in conf.conf.py
    load_secrets()

    # update os and install packages
    sudo('yum -y update', shell=False)
    for p in ['policycoreutils-python', 'wget', 'nano', 'git', 'openssl-devel', 'sqlite-devel', 'bzip2-devel', 'xz', 'gcc']:
        install_package(p)

    if PYTHON_VERSION:
        install_python(PYTHON_VERSION)

    configure_git_globals()

    # set up swap file
    sudo('dd if=/dev/zero of=/swapfile bs=1024 count=512k')
    sudo('mkswap /swapfile')
    sudo('swapon /swapfile')
    append('/etc/fstab', '/swapfile       none    swap    sw      0       0', use_sudo=True)
    sudo('chown root:root /swapfile ')
    sudo('chmod 0600 /swapfile')
    sudo('sysctl vm.swappiness=10')
    append('/etc/sysctl.conf', 'vm.swappiness=10', use_sudo=True)

    # disable postfix email service (daemon listens on port 25 by default)
    sudo('chkconfig postfix off')
    sudo('service postfix stop')

    # create non-root user
    sudo('adduser ' + USER_NAME)
    with settings(prompts = {'New password: ': env.SECRETS['server_password'],
                             'Retype new password: ': env.SECRETS['server_password']}):
        sudo('passwd ' + USER_NAME)
    sudo('echo -e "\n' + USER_NAME + '\tALL=(ALL)\tALL" >> /etc/sudoers')

    put('conf/vm/.bashrc', '/home/' + USER_NAME, mode=0754, use_sudo=True)
    sudo('chown ' + USER_NAME + ':' + USER_NAME + ' /home/' + USER_NAME + '/.bashrc')
    sudo('rm /root/.bashrc')
    sudo('ln -s /home/' + USER_NAME + '/.bashrc /root/.bashrc')

    sudo('mkdir -p ' + PROJECTS_HOME)
    sudo('chown ' + USER_NAME + ':' + USER_NAME + ' ' + PROJECTS_HOME)

    # set up firewall rules
    # flush rules
    sudo('iptables -F')
    # block null packets
    sudo('iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP')
    # prevent syn-flood attacks
    sudo('iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP')
    # drop christmas tree packets
    sudo('iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP')
    # localhost
    sudo('iptables -A INPUT -i lo -j ACCEPT')
    # SSH
    sudo('iptables -A INPUT -p tcp -m tcp --dport ' + SSH_PORT + ' -j ACCEPT')
    # web server
    sudo('iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp -m tcp --dport 443 -j ACCEPT')
    # # SMTP
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 25 -j ACCEPT')
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 465 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp -m tcp --dport 587 -j ACCEPT')
    # # POP3
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 110 -j ACCEPT')
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 995 -j ACCEPT')
    # # IMAP
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 143 -j ACCEPT')
    # sudo('iptables -A INPUT -p tcp -m tcp --dport 993 -j ACCEPT')
    # accept packets belonging to established and related connections
    sudo('iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
    # drop everything else
    sudo('iptables -P INPUT DROP')
    # allow all outgoing packets
    sudo('iptables -P OUTPUT ACCEPT')
    # disallow packet forwarding
    sudo('iptables -P FORWARD DROP')
    # save settings (they will persist on reboot)
    sudo('iptables-save | sudo tee /etc/sysconfig/iptables')
    sudo('service iptables restart')

    # set up ssh keys
    sudo('mkdir /home/' + USER_NAME + '/.ssh')
    sudo('chown ' + USER_NAME + ':' + USER_NAME + ' /home/' + USER_NAME + '/.ssh')

    put(SSH_KEY_FILE, '/tmp/id_rsa.pub', use_sudo=True)
    sudo('cat /tmp/id_rsa.pub > /home/' + USER_NAME + '/.ssh/authorized_keys')
    sudo('chown ' + USER_NAME + ':' + USER_NAME + ' /home/' + USER_NAME + '/.ssh/authorized_keys')
    sudo('rm /tmp/id_rsa.pub')
    sudo('chmod 700 /home/' + USER_NAME + '/.ssh')
    sudo('chmod 600 /home/' + USER_NAME + '/.ssh/authorized_keys')
    sudo('restorecon -Rv /home/' + USER_NAME + '/.ssh')

    # templatize sshd_config and copy to /etc/ssh/sshd_config (this will disallow root login)
    local("sed -e 's/<SSH_PORT>/" + SSH_PORT + "/g' -e 's/<USER_NAME>/" + USER_NAME + "/g' conf/vm/template.sshd_config > conf/vm/sshd_config")
    put('conf/vm/sshd_config', '/etc/ssh/sshd_config', use_sudo=True)
    local('rm conf/vm/sshd_config')
    sudo('semanage port -a -t ssh_port_t -p tcp ' + SSH_PORT) # requires policycoreutils-python package
    sudo('service sshd reload')

@task
def provision_vagrant():
    '''Assumes a clean CentOS install on a Vagrant-managed VM.'''

    # update os and install packages
    put('conf/vm/yum.conf', '/etc', use_sudo=True) # needed for kernel-devel package for vagrant
    sudo('yum -y update', shell=False)
    sudo('yum -y groupinstall development')
    for p in ['policycoreutils-python', 'wget', 'nano', 'git', 'openssl-devel', 'sqlite-devel', 'bzip2-devel', 'xz', 'gcc']:
        install_package(p)

    # install python
    if PYTHON_VERSION:
        install_python(PYTHON_VERSION)

    configure_git_globals()

    # set up swap file
    sudo('dd if=/dev/zero of=/swapfile bs=1024 count=512k')
    sudo('mkswap /swapfile')
    sudo('swapon /swapfile')
    append('/etc/fstab', '/swapfile       none    swap    sw      0       0', use_sudo=True)
    sudo('chown root:root /swapfile ')
    sudo('chmod 0600 /swapfile')
    sudo('sysctl vm.swappiness=10')
    append('/etc/sysctl.conf', 'vm.swappiness=10', use_sudo=True)

    run('chmod ugo+x /home/vagrant')
    put('conf/vm/.bashrc', '/home/vagrant', use_sudo=True)
    sudo('rm /root/.bashrc')
    sudo('ln -s /home/vagrant/.bashrc /root/.bashrc')

    sudo('echo -e "\nMatch User vagrant\n\tAllowAgentForwarding yes" >> /etc/ssh/sshd_config')

############################## Helper Functions ##############################

@task
def install_python(version):
    with cd('/usr/local/src'):
        sudo('curl -O https://www.python.org/ftp/python/{0}/Python-{0}.tar.xz'.format(version))
        sudo('tar Jxvf Python-{}.tar.xz'.format(version))
    with cd('/usr/local/src/Python-{}'.format(version)):
        sudo('./configure --prefix=/usr/local --enable-shared')
        sudo('LD_RUN_PATH=/usr/local/lib make')
        sudo('make altinstall')
    version = version[:3]
    with cd('/usr/local/lib/python{}/config'.format(version)):
        sudo('ln -s ../../libpython{}.so .'.format(version))
    sudo('echo "/usr/local/lib" >> /etc/ld.so.conf')
    sudo('ldconfig')
    # make virtualenv dir and set permissions on it (must match .bashrc)
    sudo('mkdir -p /opt/.virtualenvs')
    sudo('chown '+ USER_NAME + ':' + USER_NAME + ' /opt/.virtualenvs')
    with cd('/usr/local/src/'):
        sudo('curl https://bootstrap.pypa.io/get-pip.py -o - | /usr/local/bin/python{}'.format(version))
    sudo('/usr/local/bin/pip{} install virtualenv virtualenvwrapper'.format(version))
    sudo ('ln -s /usr/local/bin/python{} /usr/local/bin/python'.format(version))
    sudo ('ln -s /usr/local/bin/pip{} /usr/bin/pip'.format(version))