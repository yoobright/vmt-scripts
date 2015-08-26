from fabric.api import *
from fabric.colors import *
from ip_utils import *
import stack_host
import time

env.password = '111111'
env.user = 'stack'
sudo_password = '111111'

pkg_dir='/home/stack'

controller = stack_host.ctrl

cinder_hosts = stack_host.cinder

cpu_hosts = stack_host.cpu

env.roledefs = {
    'controller': controller,
    'computer': cpu_hosts,
    'cinder': cinder_hosts,
}


def my_sudo(cmd):
    global sudo_password
    with settings(password=sudo_password):
        return sudo(cmd)


@task()
def list_ip():
    print cyan("contrller:") 
    print controller
    print cyan("computer:") 
    print cpu_hosts
    print cyan("%s computer totally" % len(cpu_hosts))


@parallel(pool_size=20)
@with_settings(warn_only=True, show='debug')
def unstack():
    run("/opt/devstack/unstack.sh", timeout=120)


@task()
@roles(['cinder'])
@parallel(pool_size=20)
@with_settings(warn_only=True, show='debug')
def rm_vol():
    run("rm -rf /opt/stack/data/cinder/*")


@parallel(pool_size=20)
@with_settings(warn_only=True, show='debug')
def stack():
    run("/opt/devstack/stack.sh")


@task()
@roles(['controller', 'computer'])
@parallel(pool_size=100)
def my_reboot():
    reboot(wait=300)


@task()
@roles(['controller', 'computer'])
@parallel(pool_size=20)
def my_losetup():
    my_sudo('losetup -a')


@task()
@roles(['controller', 'computer'])
@parallel(pool_size=20)
@with_settings(warn_only=True, show='debug')
def stop_nm():
    my_sudo('service network-manager stop')
    my_sudo('apt-get -y install sysv-rc-conf')
    my_sudo('sysv-rc-conf network-manager off')


@task()
@roles(['controller', 'computer'])
@parallel(pool_size=20)
def rebuild():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo('iscsiadm -m node -u')
        my_sudo('tgt-admin --force --delete ALL')
        my_sudo('rm -rf /etc/tgt/stack.d/*')
        my_sudo('rm -rf /etc/iscsi/nodes/*')
        virsh_list_out = my_sudo("virsh list| awk '$1 ~ /[0-9]+/ {print $2}'")
        if virsh_list_out:
            instance_list = virsh_list_out.split('\r\n')
            print yellow("%s: destroy instance %s" % (env.host, instance_list))
            for instance in instance_list:
                my_sudo("virsh destroy %s" % instance)
            time.sleep(1)
        with cd(pkg_dir+'/packages/VMT-demo'):
            my_sudo("python vmt-rebuild.py")


@task()
@roles(['computer'])
@parallel(pool_size=20)
def start_tgt():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo("/etc/init.d/tgt start")


@task()
@roles(['computer', 'controller'])
@parallel(pool_size=20)
def reset_br():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo("brctl delif br100 eth1")
        my_sudo("ip link set dev br100 down")
        my_sudo("brctl delbr br100")
        #my_sudo("ip link set dev virbr0 down")
        #my_sudo("brctl delbr virbr0")
        #my_sudo("virsh net-destroy default")
        #my_sudo("virsh net-undefine default")


@task()
@roles(['computer', 'controller'])
@parallel(pool_size=20)
def reset_nova():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        run("cd /opt/stack/nova/nova/compute && cp manager.py.bak manager.py")
        run("cd /opt/stack/nova/nova/virt && cp block_device.py.bak block_device.py ")
        my_sudo("rm -rf /usr/local/lib/python2.7/dist-packages/nova*")


@task()
@roles(['computer', 'controller'])
@parallel(pool_size=20)
def set_nova():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        run("cd /opt/stack/nova/nova/compute && cp manager.py.vmthunder manager.py")
        run("cd /opt/stack/nova/nova/virt && cp block_device.py.vmthunder block_device.py")


@task()
@roles(['computer', 'controller', 'cinder'])
@parallel(pool_size=20)
def drop_database():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS nova;"')
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS cinder;"')
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS glance;"')
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS keystone;"')
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS heat;"')
        my_sudo('mysql -uroot -pnova -e "DROP DATABASE IF EXISTS neutron_ml2;"')


@task()
@roles(['computer'])
@parallel(pool_size=20)
def rm_instance():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        run("cd /home/stack/packages/VMT-demo && sh rm_instance.sh", shell=True)


@task()
@roles(['computer', 'cinder'])
@parallel(pool_size=20)
def ntpdate():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo("ntpdate 10.107.8.70")


@task()
@roles(['computer', 'controller', 'cinder'])
@parallel(pool_size=20)
def rm_log():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo('rm -rf /opt/stack/logs/*')


@task()
@roles(['cinder'])
@parallel(pool_size=20)
def rm_vol_lock():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        my_sudo("rm -rf /var/lock/lvm/*")


@task()
def unstack_ctrl():
    execute(unstack, roles=['controller'])


@task()
def unstack_cpu():
    execute(unstack, roles=['computer'])


@task()
def unstack_cinder():
    execute(rm_vol_lock)
    execute(unstack, roles=['cinder'])


@task()
def stack_ctrl():
    execute(stack, roles=['controller'])


@task()
def stack_cpu():
    execute(stack, roles=['computer'])


@task()
def stack_cinder():
    execute(stack, roles=['cinder'])


@task()
@with_settings(warn_only=True, show='debug')
def my_unstack():
    execute(unstack_cpu)
    #execute(rm_instance)
    if env.roledefs['cinder']:
        execute(unstack_cinder)
    execute(unstack_ctrl)


@task()
def my_stack():
    execute(stack_ctrl)
    if env.roledefs['cinder']:
        execute(stack_cinder)
    execute(stack_cpu)
