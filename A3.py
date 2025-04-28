
# server.py
import threading
class TupleSpace:
    #recap of the TupleSpace class
    def __init__(self):
        # dictionary mapping keys to values
        self.space = {}
        # tuple space using defaultdict
        self.lock = threading.Lock()
        
        #READ: return value if exists, else None
        def READ(self, key):
            with self.lock:
                return self.space.get(key, None)
        #GET: remove and return value if exists, else None
        def GRT(self, key):
            with self.lock:
                return self.space.get(key, None)
            # PUT: add tuple if key not present; 
            # return True if added, False if exists
        def PUT(self, key, value):
            with self.lock:
                if key in self.space:
                    return False
                self.space[key] = value
                return True
            
# socket module for TCP/IP communication
