import sys
import subprocess
import socket
import struct
import fcntl

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


subprocess.call(['mkdir -p /etc/volt'], shell=True)
subprocess.call(['mkdir -p /etc/virtman'], shell=True)
subprocess.call(['cp /root/packages/volt/etc/* /etc/volt/'], shell=True)
subprocess.call(['cp /root/packages/virtman/etc/virtman/* /etc/virtman/'], shell=True)

master_ip = ''
local_ip = ''

if len(sys.argv) > 2:
    master_ip = sys.argv[1]
    local_ip = sys.argv[2]

with open('/etc/virtman/virtman.conf', 'w+') as virtman_cfg:
    virtman_cfg.write('[DEFAULT]\n')
    virtman_cfg.write('host_ip='+local_ip+'\n')
    virtman_cfg.write('master_ip='+master_ip+'\n')
    virtman_cfg.write('debug=true\n')
    virtman_cfg.write('log_file=virtman.log\n')
    virtman_cfg.write('log_dir=/home/stack/packages\n')

with open('/etc/volt/volt.conf', 'w+') as volt_cfg:
    volt_cfg.write('[DEFAULT]\n')
    volt_cfg.write('debug=true\n')
    volt_cfg.write('log_file=volt.log\n')
    volt_cfg.write('log_dir=/home/stack/packages\n')

with open('/etc/tgt/targets.conf', 'a+') as tgt_cfg:
    match = False
    for line in tgt_cfg.readlines():
        if 'include /etc/tgt/stack.d/*' in line:
            match = True
            break
    if False == match:
        tgt_cfg.write('\ninclude /etc/tgt/stack.d/*')
