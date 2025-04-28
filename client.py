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
        packet = sock.recv(n - len(data))
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
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        #create a TCP/IP socket
        sock.connect((args.host, args.port))
        #connect to the server
        
        with open(args.file, 'r') as f:
            #open the file in binary mode
            for line in f:
                lien = line.strip()
                #strip whitespace
                if not line:
                    continue
                #skip empty lines
                parts = line.split(' ', 2)
                operation = parts[0] #operation:PUT/READ/GET
                
                #protocol establishment
                if operation == 'PUT':
                    if len(parts) < 3:
                        print(f"invalid PUT entry: {line}")
                        continue
                    # extract the key and value from the parts
                    key, value = parts[1]. parts[2]
                    if len(key) + 1 + len(value) > 970:
                        print(f"entry too long:{line}")
                        continue
                    #construct the payload of PUT
                    payload = f"P{key}{value}"
                elif operation == 'READ':
                    if len(parts) < 2:
                        print(f"invalid READ entry: {line}")
                        continue
                    # extract the key from the parts
                    key = parts[1]
                    if len(key) > 970:
                        print(f"entry too long:{line}")
                        continue
                    #construct the payload of READ
                    payload = f"R{key}"
                elif operation == 'GET':
                    if len(parts) < 2:
                        print(f"invalid GET entry: {line}")
                        continue
                    # extract the key from the parts
                    key = parts[1]
                    if len(key) > 970:
                        print(f"entry too long, skipping:{line}")
                        continue
                    #construct the payload of GET
                    payload = f"G{key}"
                else:
                    print(f"unkonwn opperation, skipping:{line}")
                    continue
                    
                    
                
            
                    
                    
                
    
        
