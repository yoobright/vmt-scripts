from fabric.api import *

env.password = '111111'
env.user = 'stack'
sudo_password = '111111'

pkg_dir='/root'

controller = ['10.107.8.180']

cinder_hosts = [
]

cpu_hosts = [
'10.107.8.170',
'10.107.8.160',
]

env.roledefs = {
    'controller': controller,
    'computer': cpu_hosts,
    'cinder': cinder_hosts,
}

def my_sudo(cmd):
    global sudo_password
    with settings(password=sudo_password):
        sudo(cmd)

@parallel(pool_size=10)
def unstack():
    run("/opt/devstack/unstack.sh", timeout=120)


@parallel(pool_size=10)
@with_settings(warn_only=True, show='debug')
def stack():
    run("/opt/devstack/stack.sh")

@task()
@parallel(pool_size=100)
def my_reboot():
    reboot(wait=300)

@task()
@roles(['controller', 'computer'])
@parallel(pool_size=10)
def my_losetup():
    my_sudo('losetup -a')

@task()
@roles(['controller', 'computer'])
@parallel(pool_size=10)
def rebuild():
    with settings(show('debug'),
                  hide('running'),
                  warn_only=True):
        virsh_list_out = my_sudo("virsh list| awk '$1 ~ /[0-9]+/ {print $2}'")
        if virsh_list_out:
            instance_list = virsh_list_out.split('\r\n')
            print instance_list
            for instance in instance_list:
                my_sudo("virsh destroy %s" % instance)
        with cd(pkg_dir+'/packages/VMT-demo'):
            my_sudo("python vmt-rebuild.py")

@task(default=True)
#@hosts(trans_hosts)
def my_unstack():
    execute(unstack, roles=['computer'])
    execute(unstack, roles=['controller'])
    execute(rebuild)

@task(default=True)
#@hosts(trans_hosts)
def my_stack():
    execute(stack, roles=['controller'])
    execute(stack, roles=['computer'])
