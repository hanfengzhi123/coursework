#FENGZHI HAN 1727533
import sys
from socket import *
from Sender1 import detach_header, BUFFER_SIZE, HEADER_SIZE

def main():
  if len(sys.argv) != 3:
    print("usage: python3 Receiver1.py Port Filename")
    return
  port, filename = sys.argv[1:]
  s = socket(AF_INET, SOCK_DGRAM)
  s.bind(('127.0.0.1', int(port)))
  print('Bind UDP on', port)
  fp = open(filename, "wb")
  while True:
    data, addr = s.recvfrom(BUFFER_SIZE + HEADER_SIZE)
    # print('Received from %s:%s' % addr)
    seq_no, eof, data = detach_header(data)
    # print(seq_no, eof, data)
    if eof:
      break
    fp.write(data)
    
  fp.close()
  s.close()


if __name__ == '__main__':
  main()
