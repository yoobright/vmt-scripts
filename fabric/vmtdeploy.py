from fabric.api import *
from fabric.contrib import files
import time

env.password = '111111'
env.user = 'root'
volt_ip = '10.107.8.180'
pkg_dir = '/home/stack'

computer_ip = [
#'10.107.8.180',
'10.107.8.170',
'10.107.8.160',
]

@task()
@hosts(computer_ip)
@parallel(pool_size=1)
def test_ls():
    run("ls -al")

@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def install_pkg():
    with settings(show('debug'),
                  #hide('running'),
                  warn_only=True
                  ):
        pkg_dir = '/root'
        with cd(pkg_dir+'/packages/'):
            run("sh install.sh")


@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def deploy_cfg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        pkg_dir = '/root'
        with cd(pkg_dir+'/packages/VMT-demo'):
            run("python vmt-initcfg.py %s %s" % (volt_ip, env.host))
        run("cat /etc/virtman/virtman.conf")

@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def deploy_cache():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        pkg_dir = '/home/stack'
        if not files.exists('%s/blocks/cache.blk' % pkg_dir):
            run("mkdir -p %s/blocks" % pkg_dir)
            run("dd if=/dev/zero of=%s/blocks/cache.blk bs=1M count=10k" %
                pkg_dir)
        run("chown -R stack:stack %s/blocks" % pkg_dir)
        run("losetup -d /dev/loop0")
        run("losetup /dev/loop0 %s/blocks/cache.blk" % pkg_dir)


@task()
@hosts(volt_ip)
@parallel(pool_size=10)
def stop_volt():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        run("start-stop-daemon  --stop -p /var/run/volt.pid")


@task()
@hosts(volt_ip)
@parallel(pool_size=10)
def run_volt():
    with settings(show('debug'),
                  hide('running'),
                  ):
        run("start-stop-daemon --start -b -m -p /var/run/volt.pid --exec"
            " /usr/local/bin/volt-api -- --config-file=/etc/volt/volt.conf",
            pty=False)
        run("ps aux | grep volt")

task()
@hosts(computer_ip)
@parallel(pool_size=10)
def stop_server():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        run("start-stop-daemon  --stop -p /var/run/virtman.pid")
        run("ps aux | grep volt")


@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def run_server():
    with settings(show('debug'),
                  hide('running'),
                  ):
        run("start-stop-daemon --start -b -m -p /var/run/virtman.pid --exec"
            " /root/packages/virtman/bin/virtmanserver.py", pty=False)
