#FENGZHI HAN 1727533
import sys
import time
from threading import Thread, Lock, Event
from socket import *

mutex = Lock()
BUFFER_SIZE = 1024  # max buffer size
next_seq, base = 0, 0


class TaskTimer(Thread):
    def __init__(self, retry_timeout):
        super().__init__()
        self.event = Event()
        self.finished = False
        self.retry_timeout = retry_timeout
        self.retry_timeout_back = retry_timeout

    def run(self):
        while not self.finished:
            while self.event.is_set() and self.retry_timeout > 0:
                time.sleep(0.1)
                self.retry_timeout -= 0.1
            if self.event.is_set():
                retransmit(self)
            time.sleep(1)
        print(">>> task timer terminated.")

    def start(self):
        """
        Start the timer.
        :return:
        """
        self.event.set()
        self.retry_timeout = self.retry_timeout_back

    def stop(self):
        """
        Stop the timer.
        :return:
        """
        self.event.clear()
        self.retry_timeout = self.retry_timeout_back

    def kill(self):
        """
        Terminate current thread.
        :return:
        """
        self.finished = True


def make_packet(seq_no, eof, data):
    """
    Attach the packet header to the given data.

    :param seq_no: sequence number - 16 bit sequence
    :param eof: 8 bit EoF flag
    :param data: data filled in the payload
    :return: data with header attached
    """
    header = bytes([seq_no >> 8, seq_no % 256, eof])

    return header + data


def parse_command():
    """
    Parse the command, exit if the commands are invalid.
    :return: <RemoteHost> <Port> <Filename> <RetryTimeout> <WindowSize>
    """
    if len(sys.argv) != 6:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <RetryTimeout> <WindowSize>")
        sys.exit(0)
    host, port, filename, retry_timeout, win_size = sys.argv[1:]

    return host, int(port), filename, int(retry_timeout), int(win_size)


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
    data = fp.read()
    fp.close()

    return data


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


def retransmit(task_timer):
    """
    Retransmit the packets from base to nextseqnum - 1.
    :param task_timer: task timer
    :return:
    """
    global base, next_seq, _skt, _content, _host, _port
    task_timer.start()
    mutex.acquire()
    lower = base
    upper = next_seq
    mutex.release()
    for i in range(lower, upper):
        offset = i * BUFFER_SIZE
        _skt.sendto(_content[offset: offset + BUFFER_SIZE], (_host, _port))
        print(">>> resend packet %d" % i)


def receive_from(task_timer):
    """
    :param task_timer: task timer
    :return:
    """
    global base, next_seq, _content, _skt
    segments = get_total_segments(_content)
    end_of_file = False
    while not end_of_file:
        mutex.acquire()
        try:
            data, _ = _skt.recvfrom(BUFFER_SIZE)
            sn1, sn2 = list(data)
            base = (sn1 << 8) + sn2
            print(">>> received ACK: %d" % base)
            if base == segments:
                end_of_file = True
            if base == next_seq:
                task_timer.stop()
            else:
                task_timer.start()
        except BlockingIOError:
            pass
        mutex.release()
        time.sleep(1)
    task_timer.kill()


def send_to(task_timer):
    """
    A sender thread to send the file to the given host.

    :param task_timer: task timer
    :return:
    """
    global next_seq, _skt, _content, _host, _port, _win_size
    segments = get_total_segments(_content)

    while True:
        mutex.acquire()
        print(">>> sender get the key...")
        if next_seq == segments:
            break
        if next_seq < base + _win_size:
            offset = next_seq * BUFFER_SIZE
            packet = make_packet(next_seq, 0, _content[offset: offset + BUFFER_SIZE])
            print(">>> send packet")
            _skt.sendto(packet, (_host, _port))
            if base == next_seq:
                task_timer.start()

        next_seq += 1
        mutex.release()
        time.sleep(1)

    # send end of file packet
    packet = make_packet(next_seq, 1, b"")
    _skt.sendto(packet, (_host, _port))


# parse the command arguments
_host, _port, _filename, _retry_timeout, _win_size = parse_command()
# read the file content
_content = read_file(_filename)
# create the socket
_skt = socket(AF_INET, SOCK_DGRAM)


def main():
    global _skt
    _skt.setblocking(0)
    task_timer = TaskTimer(_retry_timeout)
    # create send thread
    sdt = Thread(target=send_to, args=(task_timer,))
    sdt.start()
    # create receive thread
    rcv = Thread(target=receive_from, args=(task_timer,))
    rcv.start()
    # wait the sending and receive threads to terminate
    sdt.join()
    rcv.join()
    _skt.close()
    print(">>> close the socket.")


if __name__ == '__main__':
    main()
