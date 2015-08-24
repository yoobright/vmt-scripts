import re
import netaddr

ip_pattern = r'([1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])' \
             r'(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}'


def check_ip(string):
    pattern = re.compile(ip_pattern+r'\Z')
    match = pattern.match(string)
    if match:
        return True
    return False


def check_ips(string):
    pattern = re.compile(ip_pattern+'-'+ip_pattern+r':*\d*'+r'\Z')
    match = pattern.match(string)
    if match:
        return True
    return False


def handler_ip_range(string):
    step = 1
    if len(string.split(':')) > 1:
        step = int(string.split(':')[-1])
    ip_range = string.split(':')[0]
    p_boundary = ip_range.split('-')
    ip_begin = p_boundary[0]
    ip_end = p_boundary[-1]
    return map(lambda x: str(x), list(netaddr.iter_iprange(ip_begin, ip_end))[0::step])


def handler_raw_list(raw_list):
    ret_list = []
    for ip in raw_list:
        if check_ip(ip):
            ret_list.append(ip)
        if check_ips(ip):
            ret_list.extend(handler_ip_range(ip))
    return ret_list


if __name__ == '__main__':
    ip_list = list(netaddr.iter_iprange('192.0.2.1', '192.0.2.14'))
    trans_raw = ['192.0.2.1-192.0.2.110:10', '192.0.2.66']
    print ip_list
    print [str(ip) for ip in ip_list]
    print handler_ip_range('192.0.2.1-192.0.2.14')
    print handler_raw_list(trans_raw)
