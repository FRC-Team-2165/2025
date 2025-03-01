from threading import Thread, Event, Lock
import socket
import select
from time import time

from data_structures import jsonToLocation, Location

#TODO fix reconnection and errors

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
    


    @property
    def location_data(self):
        with self.data_lock:
            return self._data
    
    @location_data.setter
    def location_data(self, data: list[Location]):
        with self.data_lock:
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
        while not self.kill_threads.is_set():
            if self.listening.is_set():
                rlist, wlist, xlist = select.select([self.socket], [self.socket], [], 0.25)
                if rlist == [] and wlist == []:
                    if self.temp < 100:
                        self.temp += 1
                        continue
                    else:
                        self.error.set()
                else:
                    try:
                        self.temp = 0
                        byte_data = self.socket.recv(1)
                        if not byte_data:
                            raise IOError
                        data_id = int.from_bytes(byte_data)

                        byte_data = self.socket.recv(self.size_bytes)
                        if not byte_data:
                            raise IOError
                        size = int.from_bytes(byte_data)

                        byte_data = self.socket.recv(size)
                        if not byte_data:
                            raise IOError
                        data = byte_data.decode()

                        if data_id == self.START:
                            self.location_data = jsonToLocation(data)
                    except:
                        self.error.set()
            
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
    
    def disconnectRequest(self):
        self.LDC.disconnectRequest()
        self.LDC.kill_threads.set()
        self.disconnected.set()

    def getData(self):
        return self.LDC.location_data