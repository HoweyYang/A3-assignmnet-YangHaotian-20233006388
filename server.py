import threading
import socket
import time
import argparse


class TupleSpace:
    # recap of the TupleSpace class
    def __init__(self):
        # dictionary mapping keys to values
        self.space = {}
        # tuple space using defaultdict
        self.lock = threading.Lock()

    # READ: return value if exists, else None
    def READ(self, key):
        with self.lock:
            return self.space.get(key, None)

    # GET: remove and return value if exists, else None
    def GET(self, key):
        with self.lock:
            return self.space.pop(key, None)

    # PUT: add tuple if key not present;
    # return True if added, False if exists
    def PUT(self, key, value):
        with self.lock:
            if key in self.space:
                return False
            self.space[key] = value
            return True


def recvn(connection, n):
    """
    Helper to receive exactly n bytes or return None if EOF.
    1. Initialize an empty bytes buffer.
    2. Loop until buffer length reaches n.
    3. On each iteration, recv up to remaining bytes.
    4. If recv returns empty, connection closed: return None.
    5. Otherwise append to buffer.
    6. Return buffer when full.
    """
    data = b''  # initialize empty buffer
    while len(data) < n:  # loop until we have n bytes
        packet = connection.recv(n - len(data))
        if not packet:  # if empty bytes, peer closed
            return None
        data += packet  # accumulate received bytes
    return data  # return full buffer


def handle_client(connection, address, tuplespace, statistics):
    """
    Thread target: process requests from a single client.
    1. Loop reading messages until client closes connection.
    2. Each message: 3-byte length prefix + payload.
    3. Parse command (R/G/P), key, optional value.
    4. Update shared statistics and tuplespace accordingly.
    5. Build reply string and send with length prefix.
    6. On any exit, close connection.
    """
    try:
        while True:
            header = recvn(connection, 3)
            # read 3-byte length prefix
            if header is None:
                # connection closed
                break
            length = int(header.decode('utf-8'))
            # parse length as integer
            body = recvn(connection, length - 3)
            # read the rest of the message
            if body is None:
                # connection closed mid-message
                break
            text = body.decode('utf-8').strip()
            # decode bytes to string
            parts = text.split(' ', 2)
            # split into [command, key, value?]
            command = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            statistics['operations'] += 1
            # increment total operations

            # Handle READ command
            if command == 'READ':
                statistics['reads'] += 1
                value = tuplespace.READ(key)
                if value is None:
                    reply = f"ERR {key} does not exist"
                    statistics['errors'] += 1
                else:
                    reply = f"OK ({key}, {value}) read"

            # Handle GET command
            elif command == 'GET':
                statistics['gets'] += 1
                value = tuplespace.GET(key)
                if value is None:
                    reply = f"ERR {key} does not exist"
                    statistics['errors'] += 1
                else:
                    reply = f"OK ({key}, {value}) removed"

            # Handle PUT command
            elif command == 'PUT':
                statistics['puts'] += 1
                value = parts[2] if len(parts) > 2 else ''
                success = tuplespace.PUT(key, value)
                if success:
                    reply = f"OK ({key}, {value}) added"
                else:
                    reply = f"ERR {key} already exists"
                    statistics['errors'] += 1

            # Invalid command
            else:
                reply = "ERR invalid command"
                statistics['errors'] += 1

            # Send response back to client
            response = reply.encode('utf-8')
            # encode string to bytes
            message = f"{len(response) + 3:03d}".encode('utf-8') + response
            # prepend 3-byte length
            connection.sendall(message)
            # send entire message
    finally:
        connection.close()
        # ensure socket is closed on exit


def statistic_printer(tuplespace, statistics):
    """
    Background thread to print summary statistics every 10 seconds:
    - Number of tuples in the space.
    - Average tuple size, key size, value size.
    - Total number of clients served.
    - Total operations and breakdown: READ, GET, PUT.
    - Total error count.
    """
    while True:
        time.sleep(10)
        # pause for 10 s between reports

        # acquire lock to safely read shared tuplespace
        with tuplespace.lock:
            count = len(tuplespace.space)
            # current number of tuples
            total_size = sum(len(k) + len(v) for k, v in tuplespace.space.items())
            avg_tuple = total_size / count if count else 0
            avg_key = (sum(len(k) for k in tuplespace.space) / count) if count else 0
            avg_value = (sum(len(v) for v in tuplespace.space.values()) / count) if count else 0

        # Print formatted statistics to server stdout
        print("--- TupleSpace Statistics ---")
        print(f"Tuples: {count}, Avg size: {avg_tuple:.1f}, " + f"Avg key: {avg_key:.1f}, Avg val: {avg_value:.1f}")
        print(f"Clients: {statistics['clients']}, Operations: {statistics['operations']} " + f"(READ:{statistics['reads']} GET:{statistics['gets']} PUT:{statistics['puts']}), Errors: {statistics['errors']}\n")


if __name__ == '__main__':
    # for command-line argument parsing
    import argparse

    # define command-line interface
    parser = argparse.ArgumentParser(description="Tuple Space Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host/IP address to bind the server')
    parser.add_argument('--port', type=int, required=True, help='Port number to listen 50000-59999')
    args = parser.parse_args()

    # initialize shared tuple space and statistics dictionary
    tuplespace = TupleSpace()
    statistics = {
        'clients': 0,
        'operations': 0,
        'reads': 0,
        'gets': 0,
        'puts': 0,
        'errors': 0
    }

    # start background statistics printing thread as daemon
    threading.Thread(target=statistic_printer, args=(tuplespace, statistics), daemon=True).start()
    # create TCP socket, bind,and listen for connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((args.host, args.port))
        server_socket.listen()
        print(f"Server listening on {args.host}:{args.port}")
        # Accept and handle clients in separate threads
        while True:
            connection, address = server_socket.accept()
            # block until client connects
            statistics['clients'] += 1
            # increment client count
            threading.Thread(target=handle_client, args=(connection, address, tuplespace, statistics), daemon=True).start()
    