#FENGZHI HAN 1727533
import sys
import time
from socket import *

HEADER_SIZE = 3
BUFFER_SIZE = 1024


def make_packet(seq_no, eof, data):
    """
    Attach the packet header to the given data.

    :param seq_no: sequence number - 16 bit sequence
    :param eof: 8 bit EoF flag
    :param data: data filled in the payload
    :return: data with header attached
    """
    header = seq_no.to_bytes(2, byteorder='big') + eof.to_bytes(1, byteorder='big')

    return header + data


def extract_packet(packet):
    """
    Extract the packet.

    :param packet: packet received from the sender
    :return: sequence number, end of file flag, packet without header
    """
    sn1, sn2, eof = list(packet[:HEADER_SIZE])
    seq_no = (sn1 << 8) + sn2
    return seq_no, eof, packet[HEADER_SIZE:]


def parse_command():
    """
    Parse the command, exit if the commands are invalid.
    :return: <RemoteHost> <Port> <Filename> <RetryTimeout>
    """
    if len(sys.argv) != 5:
        print('usage: python3 Sender2.py <RemoteHost> <Port> <Filename> <RetryTimeout>')
        sys.exit(0)
    host, port, filename, retry_timeout = sys.argv[1:]

    return host, int(port), filename, int(retry_timeout)


def read_file(filename):
    """
    Read file byte to byte.
    :param filename: file needs to be sent
    :return: bytes string holds the file content
    """
    fp = open(filename, "rb")
    if not fp:
        print("Fail to open %s." % filename)
        sys.exit(0)
    content = fp.read()
    fp.close()

    return content


def get_total_segments(content):
    """
    Get total number of segments.

    :param content: file content needs to be sent
    :return:
    """
    segments = len(content) // BUFFER_SIZE  # determine number of segments required
    if len(content) % BUFFER_SIZE != 0:
        segments += 1

    return segments


def main():
    host, port, filename, retry_timeout = parse_command()
    content = read_file(filename)
    segments = get_total_segments(content)

    seq_no, retrans_no = 0, 0
    server_addr = (host, port)
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.settimeout(retry_timeout / 1000) # ms

    start = time.time()
    while seq_no != segments:
        offset = BUFFER_SIZE * seq_no
        packet = make_packet(seq_no, 0, content[offset: offset + BUFFER_SIZE])
        skt.sendto(packet, server_addr)
        # print(">>> send:", packet[:HEADER_SIZE])
        # wait for ACK
        while True:
            try:
                ack_packet = skt.recvfrom(BUFFER_SIZE)
                sn1, sn2 = list(ack_packet[0])
                ack = (sn1 << 8) + sn2
                if ack >= seq_no:
                    seq_no = ack + 1
                    break
            except timeout:
                retrans_no += 1
                time.sleep(retry_timeout / 1000)
                skt.sendto(packet, server_addr)
                # print(">>> send:", packet[:HEADER_SIZE])
    # end of file
    for i in range(3):
        packet = make_packet(seq_no, 1, b"")
        skt.sendto(packet, server_addr)
    skt.close()
    end = time.time()
    print(retrans_no, len(content) / 1024 / (end - start))


if __name__ == '__main__':
    main()
