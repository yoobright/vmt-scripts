from fabric.api import *
from fabric.colors import *
from fabric.contrib import files
import time
from ip_utils import *
import stack_host

env.password = '111111'
env.user = 'root'
volt_ip = '10.107.8.180'
pkg_dir = '/home/stack'


computer_ip = stack_host.ctrl + stack_host.cpu


@task()
def list_ip():
    print computer_ip
    print cyan("%s ip in list" % len(computer_ip))


@task()
@hosts(computer_ip)
@parallel(pool_size=1)
def test_ls():
    run("ls -al")


@task()
@hosts(computer_ip)
@parallel(pool_size=20)
def install_pkg():
    with settings(show('debug'),
                  #hide('running'),
                  warn_only=True
                  ):
        with cd(pkg_dir+'/packages/'):
            run("sh install.sh")


@task()
@hosts(computer_ip)
@parallel(pool_size=20)
def deploy_cfg():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        with cd(pkg_dir+'/packages/VMT-demo'):
            run("python vmt-initcfg.py %s %s" % (volt_ip, env.host))
        run("cat /etc/virtman/virtman.conf")

@task()
@hosts(computer_ip)
@parallel(pool_size=20)
def deploy_cache():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        #run("rm -rf %s/blocks/cache.blk" % pkg_dir)
        if not files.exists('%s/blocks/cache.blk' % pkg_dir):
            run("mkdir -p %s/blocks" % pkg_dir)
            run("dd if=/dev/zero of=%s/blocks/cache.blk bs=1M count=20k" %
                pkg_dir)
        run("chown -R stack:stack %s/blocks" % pkg_dir)
        run("losetup -d /dev/loop0")
        run("losetup /dev/loop0 %s/blocks/cache.blk" % pkg_dir)


@task()
@hosts(volt_ip)
#@parallel(pool_size=10)
def stop_volt():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        run("start-stop-daemon  --stop -p /var/run/volt.pid")
        ps_out=run("ps aux | grep volt-api | wc -l", quiet=True)
        if int(ps_out) == 2:
            print green("volt stop completed!")

@task()
@hosts(volt_ip)
#@parallel(pool_size=10)
def run_volt():
    with settings(show('debug'),
                  hide('running'),
                  ):
        run("start-stop-daemon --start -b -m -p /var/run/volt.pid --exec"
            " /usr/local/bin/volt-api -- --config-file=/etc/volt/volt.conf",
            pty=False)
        ps_out=run("ps aux | grep volt-api | wc -l", quiet=True)
        if int(ps_out) == 3:
            print green("volt start completed!")


@task()
@hosts(computer_ip)
@parallel(pool_size=20)
def stop_server():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True
                  ):
        run("start-stop-daemon  --stop -p /var/run/virtman.pid")
        run("ps aux | grep volt")


@task()
@hosts(computer_ip)
@parallel(pool_size=20)
def run_server():
    with settings(show('debug'),
                  hide('running'),
                  ):
        run("start-stop-daemon --start -b -m -p /var/run/virtman.pid --exec"
            " /root/packages/virtman/bin/virtmanserver.py", pty=False)


@task()
@hosts(stack_host.cinder + stack_host.cpu)
@parallel(pool_size=20)
def ntpdate():
    run("ntpdate %s" % stack_host.ctrl[0])


@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def su_stack():
    run("cd /opt/devstack/tools && ./create-stack-user.sh")


@task()
@hosts(computer_ip)
@parallel(pool_size=10)
def vmt_reboot():
    reboot()
