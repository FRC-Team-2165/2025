from threading import Thread, Event, Lock
import socket
import select
from time import time, sleep

from components.location_data.data_structures import jsonToLocation, Location

socket.setdefaulttimeout(1)

class LocationDataClient:
    def __init__(self, address: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.size_bytes = 4

        self.data_lock = Lock()
        self.kill_threads = Event()
        self.listening = Event()
        self.error = Event()
        self.disconnected = Event()

        self._data = []
        
        self.address = address
        self.port = port
        try:
            self.connect(self.address, self.port)
        except:
            pass

        self.START = 0
        self.STOP = 1
        self.DISCONNECT = 2
        self.STATUS = 3

        self.reconnect_delay = 0.02
        self.last_reconnect = time()

        self.temp = 0

        self.last_time = time()

        self.old_data = []
    


    @property
    def location_data(self):
        with self.data_lock:
            return self._data
    
    @location_data.setter
    def location_data(self, data: list[Location]):
        with self.data_lock:
            if data != self.old_data:
                print("updated at " + str(self.last_time - time()))
                self.last_time = time()
            self._data = data
    


    def connect(self, address: str, port: int):
        """
        connect to the location data server
        """
        try:
            self.socket.connect((address, port))
            print("connected")
        except:
            raise IOError
    
    def startRequest(self):
        """
        send the start request
        """
        try:
            self.socket.send(int(self.START).to_bytes(1))
            self.listening.set()
        except:
            self.error.set()

    def stopRequest(self):
        """
        send the stop request
        """
        try:
            self.socket.send(int(self.STOP).to_bytes(1))
            self.listening.clear()
        except:
            self.error.set()

    def disconnectRequest(self):
        """
        send the disconnect request
        """
        try:
            self.socket.send(int(self.DISCONNECT).to_bytes(1))
            self.disconnected.set()
        except:
            self.error.set()

    def statusRequest(self):
        """
        send the status request
        """
        try:
            self.socket.send(int(self.STATUS).to_bytes(1))
        except:
            self.error.set()



    def _listener_function(self):
        """
        thread function for listening for data from the location data server
        """
        buffer = bytearray(5)
        while not self.kill_threads.is_set():
            if self.error.is_set() and not self.disconnected.is_set():
                current_time = time()
                if abs(self.last_reconnect - current_time) >= self.reconnect_delay:
                    self.last_reconnect = current_time
                    try:
                        print("reconnect start")
                        self.disconnectRequest()
                        self.disconnected.clear()
                        self.socket.close()
                        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.connect(self.address, self.port)
                        self.reconnect_delay = 0.02
                        self.error.clear()
                        if self.listening.is_set():
                            self.startRequest()
                    except:
                        self.reconnect_delay = self.reconnect_delay * 2
                        print(f"error\n\nreconnect delay: {self.reconnect_delay}\n")
                        self.error.set()
                        # Failure to (re)connect implies we are not listening.
                        continue

            if self.listening.is_set():
                rlist, wlist, xlist = select.select([self.socket], [], [], 0.000001)
                if len(rlist) > 0: # implies self.socket is ready to read
                    try:
                        #  self.temp = 0
                        n_read = self.socket.recv_into(buffer, 5)
                        if n_read == 0 or buffer[0] != self.START:
                            raise IOError
                        size = int.from_bytes(buffer[1:])
                        if size > len(buffer):
                            buffer = bytearray(size);

                        bytes_read = 0
                        while bytes_read < size:
                            n = self.socket.recv_into(buffer[bytes_read:], size - bytes_read)
                            if n == 0:
                                raise IOError
                            bytes_read += n
                        #  data = byte_data.decode()
                        self.location_data = jsonToLocation(buffer[:size].decode())

                    except:
                        self.error.set()
                else:
                    sleep(0.008)
            else:
                # wait half an iteration of the robot to check if listening.
                sleep(0.01)

class LocationDataClientManager:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

        self.LDC = LocationDataClient(address, port)

        thread = Thread(target=self.LDC._listener_function)
        thread.start()

        self.listen_counter = 0
        self.disconnected = Event()
    
    def startRequest(self):
        self.listen_counter += 1
        if not self.LDC.listening.is_set():
            self.LDC.startRequest()
    
    def stopRequest(self):
        self.listen_counter -= 1
        if self.listen_counter <= 0:
            self.listen_counter = 0
            if self.LDC.listening.is_set():
                self.LDC.stopRequest()
                self.LDC.location_data = []
                print("stopped")
    
    def disconnectRequest(self):
        self.LDC.disconnectRequest()
        self.LDC.kill_threads.set()
        self.disconnected.set()

    def getData(self):
        return self.LDC.location_data
