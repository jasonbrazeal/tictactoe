from fabric.api import task, sudo, env, local, put, cd, execute
from fabric.contrib.files import sed, append

import os

from web import add_wsgi_vhost
from conf.conf import *

@task
def new():
    execute(web.add_wsgi_vhost)
    sudo ('mkdir ')


[root@dev tictactoe]# ll
total 8
-rw-r--r-- 1 root root 144 Oct 11 14:22 tictactoe.py
-rw-r--r-- 1 root root  90 Oct 11 15:12 tictactoe.wsgi
[root@dev tictactoe]# cat *
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
import sys
sys.path.insert(0, '/opt/tictactoe')

from tictactoe import app as application