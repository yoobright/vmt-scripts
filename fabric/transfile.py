import os
from fabric.api import *
from fabric.colors import *
from fabric.contrib import files
from fabric.contrib.project import rsync_project
from ip_utils import *

import stack_host

env.password = '111111'
env.user = 'root'


trans_hosts = stack_host.ctrl + stack_host.cpu + stack_host.cinder


def my_put(file_dir, chown=None):
    if not os.path.exists(file_dir):
        print "%s is not exists in local!!!" % file_dir
        return
    if not files.exists(file_dir):
        run("mkdir -p %s" % file_dir) 
    run("rm -rf %s" % os.path.join(file_dir, '*'))
    put(os.path.join(file_dir, '*'), file_dir, mirror_local_mode=True)
    if len([f for f in os.listdir(file_dir) if f.startswith('.')]) > 0:
        print yellow("upload hidden files...")
        put(os.path.join(file_dir, '.*'), file_dir, mirror_local_mode=True)
    if chown:
        run("chown -R %s %s" % (chown, file_dir))


def my_sync(file_dir):
    if os.path.isdir(file_dir):
        print cyan("rsync %s" % file_dir)
        print env.host_string
        local("sshpass -p %s rsync  -avzrtopgL --delete %s/* %s@%s:%s" %
              (env.password, file_dir, env.user, env.host_string, file_dir))
        #rsync_project(file_dir, local_dir='%s/*' % file_dir,
        #              default_opts="-avzrtopgL --delete")
    else:
        put(file_dir, file_dir, mirror_local_mode=True)


@task()
def list_ip():
    print trans_hosts
    print cyan("%s ip in list" % len(trans_hosts))


@task()
@hosts(trans_hosts)
@parallel(pool_size=20)
def root_pkg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/root/packages/')


@runs_once
def cp_pkg():
    local('cp -r /root/packages/ /home/stack')


@task()
@hosts(stack_host.ctrl + stack_host.cpu)
@parallel(pool_size=20)
def virtman():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/home/stack/packages/virtman', chown='stack:stack')
        run('cd /home/stack/packages/virtman && python setup.py install')


@task()
@hosts(stack_host.cpu + stack_host.cinder)
@parallel(pool_size=20)
def nova():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sync('/opt/stack/nova')


@hosts(trans_hosts)
@parallel(pool_size=20)
def do_stack_pkg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/home/stack/packages/', chown='stack:stack')


@task()
@hosts(trans_hosts)
@parallel(pool_size=20)
def dev_lib():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sync('/opt/devstack/lib')


@task()
@hosts(trans_hosts)
@parallel(pool_size=20)
def script():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/home/stack/packages/VMT-demo', chown='stack:stack')


@task()
@hosts(trans_hosts)
@parallel(pool_size=20)
def stack_pkg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/home/stack/packages/', chown='stack:stack')
        #my_sync('/home/stack/packages')


@task()
@hosts(trans_hosts)
@parallel(pool_size=20)
def opt_stack():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_put('/opt/stack/nova', chown='stack:stack')
        my_put('/opt/stack/python-novaclient', chown='stack:stack')
        my_put('/opt/stack/horizon', chown='stack:stack')
        run("cd /opt/stack/nova && python setup.py install")
        run("cd /opt/stack/python-novaclient && python setup.py install")
        run("cd /opt/stack/horizon && python setup.py install")
        my_put("/opt/devstack/lib", chown='stack:stack')

