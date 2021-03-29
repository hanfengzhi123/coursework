#FENGZHI HAN 1727533
import sys
from socket import *

HEADER_SIZE = 3
BUFFER_SIZE = 1024


def attach_header(seq_no, eof, data):
  """
  Attach the packet header to the given data.

  :param seq_no: sequence number - 16 bit sequence
  :param eof: 8 bit EoF flag
  :param data: data filled in the payload
  :return: data with header attached
  """
  header = bytes([seq_no >> 8, seq_no % 256, eof])

  return header + data


def detach_header(data):
  """
  Attach the packet header to the given data.

  :param data: data received from the sender
  :return: sequence number, end of file flag, cleaned data
  """
  sn1, sn2, eof = list(data[:3])
  seq_no = sn1 << 8 + sn2
  return seq_no, eof, data[3:]


def main():
  if len(sys.argv) != 4:
    print("usage: python3 Sender1.py RemoteHost Port Filename")
    return
  host, port, filename = sys.argv[1:]
  
  seq_no = 0
  s = socket(AF_INET, SOCK_DGRAM)
  try:
    fp = open(filename, "rb")
    while True:
      eof = 0
      buf = fp.read(BUFFER_SIZE)
      if not buf:
        eof = 1
        data = attach_header(seq_no, eof, b"")
      else:
        data = attach_header(seq_no, eof, buf)
      s.sendto(data, (host, int(port)))
      if eof:
        break
    fp.close()
  except FileNotFoundError:
    print("Fail to find", filename)

  s.close()


if __name__ == '__main__':
  main()