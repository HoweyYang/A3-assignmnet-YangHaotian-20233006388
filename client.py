#client.py
import socket   # for TCP/IP sockets
import argparse # for command-line parsing
import os       # for file existence check
import sys      # for sys.exit

def recvn(sock, n):
    """
    Helper to recieve exactly n bytes or return None if EOF.
    Same logic as server's recvn
    Args:sock (socket.socket): The socket object from which to receive data.
    n (int): The number of bytes to receive.
    Returns: bytes: The received data of length n if successful, None otherwise.
    
    """
    data = b''
    while len(data) < n:
        packet = sock.recieve(n - len(data))
        if not packet:
            #if empty bytes, peer closed
            return None
        data += packet
    return data
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Tuple Space Client')
    parser.add_argument('host', help = 'Server hostname or Ip address')
    parser.add_argument('port', type = int, help = 'Server port number')
    parser.add_argument('file', help = 'Path to the request file')
    #parse command-line arguments
    args = parser.parse_args()
    
    #check if file exists
    if not os.path.isfile(args.file):
        print(f"File{args.file} does not exist")
        sys.exit(1)
    
        
