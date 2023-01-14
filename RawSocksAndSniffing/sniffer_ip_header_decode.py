import ipaddress
import os
import socket
import struct
import sys

# Format types
# B -> unsigned char
# H -> unsigned short
# s -> char[] hence 4s -> 4 byte string


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


def sniff(host):
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(
        socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    # Include the IP headers in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # read a packet
            # asssigns the first element of tuple(bytes)
            raw_buffer = sniffer.recvfrom(65535)[0]
            # create an IP Header from the first 20 bytes
            ip_header = IP(raw_buffer[0:20])
            # print the detected protocol and hosts
            print(
                f'Protocol {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}')

    except KeyboardInterrupt:
        # if we are on Windows, turns of promiscuous mode
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '10.0.2.15'
    sniff(host)
