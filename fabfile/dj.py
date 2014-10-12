import logging
import sys
import json

from fabric.api import task, sudo, env, local, run, put, cd, prefix, hosts, lcd, execute, path, settings, with_settings
from fabric.contrib.files import sed, append
from fabric.operations import get

from conf.conf import *

env.hosts = ['']

LOG = logging.getLogger(__name__)

PROJECTS_HOME_ESC = sed_escape(PROJECTS_HOME)
PROJECT_DIR_ESC = sed_escape(PROJECT_DIR)

@task
def new_do(environment, project=PROJECT_NAME, django_project=None):
    '''Starts a new Django project. environment must be "dev" or "prod" and will determine things like which requirements and settings files are used, wsgi configuration, etc.
    '''
    load_secrets()

    if django_project == None:
        django_project = project

    WORKON_HOME = run('echo $WORKON_HOME')
    WORKON_HOME_ESC = sed_escape(WORKON_HOME)
    DJANGO_PROJECT_DIR = PROJECT_DIR + '/' + django_project

    # set up virtualenv
    sudo('mkdir -p ' + PROJECT_DIR)
    sudo('chown {}:{} {}'.format(USER_NAME, USER_NAME, PROJECT_DIR))
    sudo('chmod ugo+x ' + PROJECT_DIR)
    run('mkvirtualenv -a ' + PROJECT_DIR + ' ' + project)
    run('setvirtualenvproject ' + PROJECT_DIR + ' ' + PROJECT_DIR) # set project folder same as virtualenv folder

    # make requirements folder copy files to vm
    run('mkdir -p ' + DJANGO_PROJECT_DIR + '/requirements')

    put('conf/dj/requirements/base.txt', DJANGO_PROJECT_DIR + '/requirements')
    put('conf/dj/requirements/' + environment + '.txt', DJANGO_PROJECT_DIR + '/requirements')

    # install django and other required packages
    with prefix('workon ' + project):
        run('pip install -r ' + DJANGO_PROJECT_DIR + '/requirements/' + environment + '.txt')

    # create a new django project
    run(WORKON_HOME + '/' + project + '/bin/django-admin.py startproject ' + django_project + ' ' + PROJECT_DIR)

    # templatize wsgi.conf and copy to to vm
    local("sed -e 's/<WORKON_HOME>/"+ WORKON_HOME_ESC + "/g' -e 's/<PROJECT_DIR>/" + PROJECT_DIR_ESC + "/g' -e 's/<ENV>/" + environment + "/g' -e 's/<HOSTNAME_PROD>/" + HOSTNAME_PROD + "/g' -e 's/<HOSTNAME_DEV>/" + HOSTNAME_DEV + "/g' -e 's/<PROJECT>/" + django_project + "/g' conf/dj/template_" + environment + ".wsgi.conf > conf/dj/wsgi.conf")
    put('conf/dj/wsgi.conf', '/etc/httpd/conf.d', use_sudo=True)

    # templatize wsgi.py and copy to to vm
    local("sed -e 's/<WEBAPP>/"+ project + "/g' -e 's/<PROJECT>/" + django_project + "/g' -e 's/<ENV>/" + environment + "/g' -e 's/<PROJECT_DIR>/" + PROJECT_DIR_ESC + "/g' conf/dj/template.wsgi.py > conf/dj/wsgi.py")
    put('conf/dj/wsgi.py', DJANGO_PROJECT_DIR, use_sudo=True)

    # templatize manage.py and copy to to vm
    local("sed -e 's/<WEBAPP>/"+ project + "/g' -e 's/<PROJECT>/" + django_project + "/g' -e 's/<ENV>/" + environment + "/g' conf/dj/template.manage.py > conf/dj/manage.py")
    put('conf/dj/manage.py', PROJECT_DIR, use_sudo=True)

    # create logs
    run('mkdir -p ' + PROJECT_DIR + '/log')
    with cd(PROJECT_DIR + '/log'):
        run('touch access_' + project + '.log')
        run('touch error_' + project + '.log')

    # templatize settings files and copy to vm
    local("sed -e 's/<PROJECT_DIR>/" + PROJECT_DIR_ESC + "/g' -e 's/<PROJECT>/" + django_project + "/g' conf/dj/settings/template.base.py > conf/dj/settings/base.py")
    local("sed -e 's/<PROJECT_DIR>/" + PROJECT_DIR_ESC + "/g' -e 's/<PROJECT>/" + django_project + "/g' conf/dj/settings/template." + environment + ".py > conf/dj/settings/" + environment + ".py")

    # remove settings.py created by django
    with cd(DJANGO_PROJECT_DIR):
      run('rm settings.py')

    # set up settings folder
    run('mkdir ' + DJANGO_PROJECT_DIR + '/settings')
    with lcd('conf/dj/settings'):
      put('base.py', DJANGO_PROJECT_DIR + '/settings')
      put(environment + '.py', DJANGO_PROJECT_DIR + '/settings')
    with cd(DJANGO_PROJECT_DIR + '/settings'):
        run('touch __init__.py')
    deploy_secrets(environment, project)

    # copy other essential files to vm, create essential folders
    put('conf/dj/.gitignore', DJANGO_PROJECT_DIR)
    put('conf/dj/urls.py', DJANGO_PROJECT_DIR)
    with cd(DJANGO_PROJECT_DIR):
        run('touch README.md')
        run('touch LICENSE.txt')
        run('mkdir tests')
        run('mkdir doc')
        run('mkdir apps')
        run('touch apps/__init__.py')

    # remove templatized files from conf folder
    with lcd('conf/dj'):
        local('rm wsgi.conf wsgi.py manage.py')
    with lcd('conf/dj/settings'):
        local('rm base.py ' + environment + '.py')
    from web import restart_apache
    execute(restart_apache)

@task
def deploy_secrets(environment, project, django_project=None):
    if django_project == None:
        django_project = project
    DJANGO_PROJECT_DIR = PROJECT_DIR + '/' + django_project

    if not env.get('SECRETS', False):
        load_secrets()

    with cd(DJANGO_PROJECT_DIR + '/settings'):
        # add secret key and db info
        append(environment + '.py', "SECRET_KEY = '" + env.SECRETS['dj_secret_key'] + "'")
        append(environment + '.py', "DATABASES = {'default': {'ENGINE': '" + env.SECRETS.get('dj_db_engine', '') + "', 'NAME': '" + env.SECRETS.get('dj_db_name', '') + "', 'USER': '" + env.SECRETS.get('dj_db_user', '') + "', 'PASSWORD': '" + env.SECRETS.get('dj_db_user_password', '') + "', 'HOST': '" + env.SECRETS.get('dj_db_host', '') + "', 'PORT': '" + env.SECRETS.get('dj_db_port', '') + "'}}")

@task
def deploy_project(environment, project, django_project=None):
    if django_project == None:
        django_project = project
    DJANGO_PROJECT_DIR = PROJECT_DIR + '/' + django_project

    if not env.get('SECRETS', False):
        load_secrets()

    with cd(DJANGO_PROJECT_DIR):
        run('rm -rf .[^.] .??*')
        put(django_project, PROJECT_DIR)
        run('find . -name "*.pyc" -delete')

    execute(deploy_secrets, environment, project)

@task
def startapp(project, django_project=None, app=None):
    if django_project == None:
        django_project = project
    if app == None:
        app = django_project + '_app'

    DJANGO_PROJECT_DIR = PROJECT_DIR + '/' + django_project
    APP_DIR = DJANGO_PROJECT_DIR + '/apps/' + app

    run('mkdir -p ' + APP_DIR)

    with prefix('workon ' + project):
        run('python manage.py startapp ' + app + ' ' + APP_DIR)
    with cd(APP_DIR):
        run('mkdir -p templates/' + app)
        run('mkdir -p static/' + app + '/css')
        run('mkdir -p static/' + app + '/js')
        run('mkdir -p static/' + app + '/img')
    with cd(DJANGO_PROJECT_DIR + '/apps'):
        run('touch __init__.py')
    with cd(DJANGO_PROJECT_DIR + '/settings'):
        run('echo "INSTALLED_APPS += (\'' + django_project + '.apps.' + app + '\',)" >> base.py')

@task
def startapp_shared(project, django_project=None, app='shared'):
    if django_project == None:
        django_project = project

    DJANGO_PROJECT_DIR = PROJECT_DIR + '/' + django_project
    APP_DIR = DJANGO_PROJECT_DIR + '/apps/' + app

    startapp(project, django_project, app)

    with cd(APP_DIR):
        run('mkdir templatetags')
    with cd(APP_DIR + '/templatetags'):
        run('touch __init__.py')
        run('touch filters.py')
        run('touch tags.py')
    with cd(APP_DIR + '/templates/' + app):
        run('touch 404.html')
        run('touch 500.html')

@task
def collectstatic(project):
    with cd('/opt/' + project):
        with prefix('workon ' + project):
            with settings(prompts = {"Type 'yes' to continue, or 'no' to cancel: ": 'yes'}):
                sudo('python manage.py collectstatic')

@task
def setup_sqlite_db(project):
    sudo('mkdir /var/www/db')
    sudo('chown apache:apache /var/www/db')
    execute(syncdb, project)
    sudo('chmod 764 /var/www/db/' + project + '.db')

@task
def syncdb(project):
    with cd('/opt/' + project):
        with prefix('workon ' + project):
            sudo('python manage.py syncdb')

@task
def runserver(project):
    '''Runs the django development server on the VM, accessible by pointing the host's browser to http://localhost:8008
    '''
    with prefix('workon ' + project):
        run('python manage.py runserver 0.0.0.0:8000') # allows you to request django pages at localhost:8008 on the host machine
        # run('python manage.py runserver [::]:8000') # IPv6 variation