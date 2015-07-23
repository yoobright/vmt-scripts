import os
from fabric.api import *
from fabric.contrib import files

env.password = '111111'
env.user = 'root'

trans_hosts = [
'10.107.8.170',
'10.107.8.160',
]

def my_put(file_dir, chown=None):
    if not os.path.exists(file_dir):
        print "%s is not exists in local!!!" % file_dir
        return
    if not files.exists(file_dir):
        run("mkfile_dir %s" % file_dir) 
    run("rm -rf %s" % os.path.join(file_dir, '*'))
    put(os.path.join(file_dir, '*'), file_dir, mode=0755)
    put(os.path.join(file_dir, '.*'), file_dir, mode=0755)
    if chown:
        run("chown -R %s %s" % (chown, file_dir))


@task()
@hosts(trans_hosts)
@parallel(pool_size=10)
def root_pkg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/root/packages/')


@task()
@hosts(trans_hosts)
@parallel(pool_size=10)
def opt_pkg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/opt/stack/nova', chown='stack:stack')
        my_put('/opt/stack/python-novaclient', chown='stack:stack')
        my_put('/opt/stack/horizon', chown='stack:stack')
        run("cd /opt/stack/nova && python setup.py install")
        run("cd /opt/stack/python-novaclient && python setup.py install")
        run("cd /opt/stack/horizon && python setup.py install")

