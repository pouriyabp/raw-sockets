import struct
import socket
import sys
import os
# ======================================================================================================================
# ICMP protocol
ICMP_ECHO_REQUEST = 8


def crate_packet(identifier, sequence_number=1, packet_size=10):  # default packet size is 10 byte.
    # Maximum for an unsigned short int c object counts to 65535(0xFFFF). we have to sure that our packet id is not
    # greater than that.
    identifier = identifier & 0xFFFF

    # cod is 0 for icmp echo request
    code = 0
    # checksum is 0 for now
    checksum = 0
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, code, checksum, identifier, sequence_number)
    # Payload Generation
    payload_byte = []
    if packet_size > 0:
        for i in range(0x42, 0x42 + packet_size):  # 0x42 = 66 decimal
            payload_byte += [(i & 0xff)]  # Keep chars in the 0-255 range
    data = bytes(payload_byte)
    checksum = calculate_checksum(header + data)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, code, checksum, identifier, sequence_number)
    packet = header + data
    return packet


# copy form github https://github.com/Akhavi/pyping/blob/master/pyping/core.py with few changes.
# The checksum calculation is as follows RFC1071 (https://tools.ietf.org/html/rfc1071)
def calculate_checksum(source_string):
    countTo = (int(len(source_string) / 2)) * 2
    sum = 0
    count = 0

    # Handle bytes in pairs (decoding as short ints)
    loByte = 0
    hiByte = 0
    while count < countTo:
        if (sys.byteorder == "little"):
            loByte = source_string[count]
            hiByte = source_string[count + 1]
        else:
            loByte = source_string[count + 1]
            hiByte = source_string[count]
        sum = sum + (hiByte * 256 + loByte)
        count += 2

    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if countTo < len(source_string):  # Check for odd length
        loByte = source_string[len(source_string) - 1]
        sum += loByte

    sum &= 0xffffffff  # Truncate sum to 32 bits (a variance from ping.c, which
    # uses signed ints, but overflow is unlikely in ping)

    sum = (sum >> 16) + (sum & 0xffff)  # Add high 16 bits to low 16 bits
    sum += (sum >> 16)  # Add carry from above (if any)
    answer = ~sum & 0xffff  # Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer


class IcmpPacket:
    def __init__(self, packet_size=0):
        self.type = ICMP_ECHO_REQUEST
        self.code = 0
        self.checksum = 0
        self.id = os.getpid()
        self.sequence = 0
        self.packet_size = packet_size