#FENGZHI HAN 1727533
import sys
import time
from socket import *


BUFFER_SIZE, HEADER_SIZE = 1024, 3


def extract_packet(packet):
    """
    Extract the packet.

    :param packet: packet received from the sender
    :return: sequence number, end of file flag, packet without header
    """
    sn1, sn2, eof = list(packet[:HEADER_SIZE])
    seq_no = (sn1 << 8) + sn2
    return seq_no, eof, packet[HEADER_SIZE:]


def main():
    if len(sys.argv) != 3:
        print("usage: python3 Receiver3.py Port Filename")
        return
    port, filename = sys.argv[1:]
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('127.0.0.1', int(port)))
    # print('>>> bind UDP on', port)
    fp = open(filename, "wb")
    prev_seq, cur_seq = 0, 0
    while True:
        packet, addr = s.recvfrom(BUFFER_SIZE + HEADER_SIZE)
        seq_no, eof, data = extract_packet(packet)
        print(">>> sequence number:", cur_seq, seq_no)
        if cur_seq == seq_no:
            if eof:
                break
 
            fp.write(data)
            s.sendto(cur_seq.to_bytes(2, byteorder='big'), addr)
            prev_seq = cur_seq
            cur_seq += 1
        else:
            s.sendto(prev_seq.to_bytes(2, byteorder='big'), addr)

    fp.close()
    s.close()
    # print(">>> end of transmit")


if __name__ == '__main__':
    main()
