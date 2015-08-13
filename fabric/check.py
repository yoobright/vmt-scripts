from fabric.api import *
from fabric.colors import *
from ip_utils import *

import stack_host
env.password = '111111'
env.user = 'root'


trans_hosts = stack_host.ctrl + stack_host.cpu

dm_exist_list = []
loop_not_exist_list = []


@task()
def list_ip():
    print trans_hosts
    print cyan("%s ip in list" % len(trans_hosts))

@hosts(trans_hosts)
#@parallel(pool_size=1)
def check_dm():
    with settings(#show('debug'),
                  hide('running'),
                  warn_only=True):
        global dm_exist_list
        dm_out = run("dmsetup table | grep cache_fcg") or None
        if dm_out is not None:
            dm_exist_list.append(env.host)

@task()
@hosts(trans_hosts)
#@parallel(pool_size=1)
def check_date():
    with settings(#show('debug'),
                  hide('running'),
                  warn_only=True):
        run("date")


@task()
def check_dm_clean():
    global dm_exist_list
    execute(check_dm)
    if dm_exist_list:
        print yellow("fcg dm exist")
        print dm_exist_list
    else:
        print green("fcg dm clean")
    
        
@hosts(trans_hosts)
#@parallel(pool_size=1)
def check_loop():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        global loop_not_exist_list 
        loop_out = run("losetup -a | grep cache.blk") or None
        if not loop_out:
            loop_not_exist_list.append(env.host)

@task()
def check_loop_exist():
    global loop_not_exist_list 
    execute(check_loop)
    if loop_not_exist_list:
        print yellow("loop not exist")
        print loop_not_exist_list
    else:
        print green("loop cache exist")

