import ipaddress
import os
import socket
import struct
import sys
import threading
import time

# subnet to target
SUBNET = '172.23.0.0/16'
# magic string we'll check ICMP responses for
MESSAGE = 'PYTHONRULES!'


class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)

        self.ver = header[0] >> 4   # assigning the ver  to first nibble
        self.ihl = header[0] & 0xF  # assigning the ihl to last nibble

        self.tos = header[1]    # unsigned char
        self.len = header[2]  # unsigned short
        self.id = header[3]     # unsigned short
        self.offset = header[4]    # unsigned short
        self.ttl = header[5]    # unsigned char
        self.protocol_num = header[6]  # unsigned char
        self.sum = header[7]    # unsigned short
        self.src = header[8]  # 4 byte string
        self.dst = header[9]    # 4 byte stringe

        # human readable ip addresses
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # setting the protocol type
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print(f'{e} No protocol for {self.protocol_num}')


class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]


def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))


class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket_protocol)

        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                # read a packet
                raw_buffer = self.socket.recvfrom(65535)[0]
                # create an IP header from the first 20 bytesE
                ip_header = IP(raw_buffer[:20])
                # checking if the ICMP response is coming from within our target subnet,
                if ip_header.protocol == 'ICMP':
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)
                    # need to check for TYPE 3 and CODE
                    if icmp_header.type == 3 and icmp_header.code == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            # make sure it has our magic message
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf-8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f'Host up: {tgt}')

        # handle CTRL-C
        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

            print('\nUser interrupted.')
            if hosts_up:
                print(f'\n\nSummary: Hosts up on {SUBNET}')
            for host in sorted(hosts_up):
                print(f'{host}')
                print('')
            sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:  # if there is one argument passed in the cli
        host = sys.argv[1]
    else:
        host = '172.23.106.252'
    s = Scanner(host)
    time.sleep(5)
    # spawning the udp_sender in a different thread for not causing the interfere with sniff action
    t = threading.Thread(target=udp_sender())
    t.start()
    s.sniff()
