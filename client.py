import socket
import threading
import time
import atexit
from secrets import token_hex


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.connected = False
        self.name = token_hex(4)
        print(f'Client {self.name} started')

    def run(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                if data == b'connected' and not self.connected:
                    self.connected = True
                    print(f'Connected to server {addr}')
                    print("-" * 91)
                else:
                    text = data.decode('utf-8')
                    other_name = text[:8]
                    content = text[8:]
                    length = 32
                    lines = []
                    count = 0
                    temp = ''
                    for char in content:
                        if char == '\n':
                            lines.append(temp + ' ' * (length - count))
                            temp = ''
                            count = 0
                            continue
                        temp += char
                        count += 1 if ord(char) < 8000 else 2
                        if count == length:
                            lines.append(temp)
                            temp = ''
                            count = 0
                        elif count == length - 1:
                            lines.append(f'{temp} ')
                            temp = ''
                            count = 0
                    if temp:
                        lines.append(temp + ' ' * (length - count) + f" |{'|':=>45}")
                    print(f"\n[{other_name}]", f" |{'|':=>45}\n           ".join(lines) + f"\n{'|':>45} ", end='')
            except:
                pass
            time.sleep(0.01)

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.thread.join()
        self.socket.close()
        print('\nClient stopped')

    def send(self, m: str):
        m = self.name + m
        m = m.replace("\\n", "\n")
        self.socket.sendto(m.encode('utf-8'), (self.host, self.port))


if __name__ == '__main__':
    host = input("input server's host (localhost default): ").lstrip('\r')
    host = host or 'localhost'
    port = input("input server's port (8888 default): ").lstrip('\r')
    port = int(port) if port else 8888
    client = Client(host, port)
    atexit.register(client.stop)
    try:
        while not client.connected:
            client.send('connect')
            time.sleep(0.1)
        while True:
            if msg := input(f"{'|':>45}{'|':=>45}\n{'|':>45} ").lstrip('\r'):
                client.send(msg)
    except KeyboardInterrupt:
        client.stop()
