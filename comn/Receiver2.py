#FENGZHI HAN 1727533
import sys
import time
from socket import *
from Sender2 import extract_packet, BUFFER_SIZE, HEADER_SIZE


def main():
    if len(sys.argv) != 3:
        print("usage: python3 Receiver2.py Port Filename")
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
        #print(">>> sequence number:", cur_seq, seq_no)
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
