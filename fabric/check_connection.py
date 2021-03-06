import socket
import threading
import stack_host

MAX_THREAD = 10

check_ips = stack_host.ctrl + stack_host.cpu + stack_host.cinder


def check_connection(ip):
    check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check_socket.settimeout(0.5)
    try:
        check_socket.connect((ip, 22))
    except Exception, e:
        check_socket.close()
        return False
    check_socket.close()
    return True


def add_failed_ip(ip, failed_ip_list=[]):
    if not check_connection(ip):
        failed_ip_list.append(ip)


if __name__=='__main__':
    failed_ip_list = []
    index = 0
    while index < len(check_ips):
        thread_number = min(MAX_THREAD, len(check_ips)-index)
        thread_list = []
        for thread_id in range(thread_number):
            thread = threading.Thread(target=add_failed_ip,
                                      args=(check_ips[index], failed_ip_list))
            thread.start()
            thread_list.append(thread)
            index += 1
        for thread in thread_list:
            thread.join()
    if not failed_ip_list:
        print "all %s ips connect success" % len(check_ips)
    else:
        print "failed_ip_list = %s" % failed_ip_list
        print "failed %s node" % len(failed_ip_list)
