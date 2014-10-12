# Project Starter Scripts

These are some scripts I use when starting and deploying projects of different types. They use Fabric and Vagrant to set up a new CentOS VM for the project and perform some initial configuration. Feel free to fork this repo if you find something useful for you.

### Vagrantfile for starting a new project on a Vagrant-managed VM

Standard Vagrantfile with a few extras like naming the VM based on the project name.

### Fabfile collection for starting and managing new projects

The project configuration is contained in constants in conf/conf.py. These should be set up for any new project.
There are environment setters in fabfile/___init__.py that will set the environment to dev, prod, (written by me) or vagrant (from fabtools package) before performing a task. For example, to start apache on a local vagrant machine, `fab vagrant web.start_apache`. To install apache on a production server, `fab prod web.provision_apache`. Note that the provisioning functions that initially set up the system (adding a non-root user, configuring ssh, etc.) must be run with the setters "dev_setup" or "prod_setup". So to set up a Digital Ocean CentOS development machine from scratch, create the image online then run:
`fab dev_setup vm.provision_do` <--secures machine, changes ssh, firewall, etc.
`fav dev web.provision_apache`  <--installs apache
`fav dev web.test_apache`       <--creates test.html at path specified in conf.conf.APACHE_DOCUMENT_ROOT

To see a list of available commands, run `fab --list`:

dev
dev_setup
install_package
prod
prod_setup
replace_in_file
vagrant
db.mysql.backup
db.mysql.create
db.mysql.install_package
db.mysql.replace_in_file
db.mysql.restart
db.mysql.restore
db.mysql.setup
db.mysql.start
db.mysql.stop
dj.collectstatic
dj.install_package
dj.new_django
dj.new_do
dj.replace_in_file
dj.runserver
dj.startapp
dj.startapp_shared
dj.syncdb
dj.testapp
git.initialize
git.install_package
git.replace_in_file
vm.install_package
vm.install_python
vm.provision_do
vm.provision_vagrant
vm.replace_in_file
web.add_vhost
web.install_package
web.provision_apache
web.provision_php
web.replace_in_file
web.reset_httpd_conf
web.restart_apache
web.start_apache
web.stop_apache
web.test_html
web.test_php
wp.install_package
wp.new
wp.replace_in_file
wp.setup_wp_config

### Requirements
* Python
* Python Packages: Fabric, fabtools
* Vagrant (vagrant-vbguest plugin highly recommended)
* Virtualbox

### Troubleshooting
* If the shared folders don't mount the first time you start the VM, just update the software on the VM (with `fab vagrant vm.provision_vagrant`) then reload the VM (with `vagrant reload`). It's OK if `fab vagrant vm.provision_vagrant` fails the first time; just be sure to rerun it after the VM is reloaded.

* Fatal error: Host key for 0.0.0.0 did not match pre-existing key! Server's key was changed recently, or possible man-in-the-middle attack.
  * fix: delete ~/.ssh/known_hosts on your local machine