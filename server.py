import socket
import time
import threading
import atexit
from collections import deque


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.setblocking(False)
        self.clients = []
        self.records = deque(maxlen=100)
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print('Server started at', self.socket.getsockname())

    def run(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                name = data.decode('utf-8')[:8]
                if addr not in self.clients:
                    self.clients.append(addr)
                    print(f'New client {name} {addr} connected')
                    self.socket.sendto(b'connected', addr)
                    for record in self.records:
                        self.socket.sendto(record, addr)
                    continue
                print(f'Received message from client {name}')
                self.records.append(data)
                for client in self.clients:
                    if client != addr:
                        self.socket.sendto(data, client)
            except:
                pass
            time.sleep(0.01)

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.records.clear()
        self.clients.clear()
        self.thread.join()
        self.socket.close()
        print('\nServer stopped')


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        print('[warning] Cannot get the IP address, used localhost instead')
        IP = 'localhost'
    finally:
        st.close()
    return IP


if __name__ == '__main__':
    host = input("Is server public? (default no): ").lstrip('\r')
    host = extract_ip() if host.lower().startswith('y') else "localhost"
    port = input("input port (8888 default): ").lstrip('\r')
    port = int(port) if port else 8888
    server = Server(host, port)
    atexit.register(server.stop)
    try:
        print("enter .exit to terminate the server")
        print("enter .clear to clear records")
        print("enter .clearall to clear records and saved clients")
        while True:
            if msg := input(">>>\n").lstrip('\r'):
                if msg == '.exit':
                    break
                if msg == '.clearall':
                    server.records.clear()
                    server.clients.clear()
                    continue
                if msg == '.clear':
                    server.records.clear()
                    continue
                msg = f"-Server-{msg}"
                for client in server.clients:
                    server.socket.sendto(msg.encode('utf-8'), client)
    finally:
        server.stop()
