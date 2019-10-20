import os
import re
import socket
import socketserver
import threading
import timeit
from queue import Queue, Empty
# import necessary module
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np


class ThreadingPoolMixIn:
    """Mix-in class to handle each request in a new thread."""

    # Decides how threads will act upon termination of the
    # main process
    daemon_threads = False
    # If true, server_close() waits until all non-daemonic threads terminate.
    block_on_close = True
    _threads = None
    numThreads = 5
    requests = None
    isClose = False

    def server_activate(self):
        self.requests = Queue(self.numThreads)
        self._threads = []
        for x in range(self.numThreads):
            t = threading.Thread(target=self.process_request_queue)
            self._threads.append(t)
            t.setDaemon(True)
            t.start()
        socketserver.TCPServer.server_activate(self)

    def process_request_queue(self):
        while not self.isClose:
            try:
                t = [*self.requests.get(timeout=1)]
                self.process_request_thread(*t)
            except Empty:
                pass

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.

        """
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        self.requests.put((request, client_address))

    def server_close(self):
        super().server_close()
        if self.block_on_close:
            threads = self._threads
            self._threads = None
            self.isClose = True
            if threads:
                for thread in threads:
                    thread.join()


class ThreadPoolTCPServer(ThreadingPoolMixIn, socketserver.TCPServer):
    pass


class MyTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):
        try:
            while True:
                msg_len_bytes = self.request.recv(4)
                msg_len = int.from_bytes(msg_len_bytes, byteorder="big")
                msg_bytes: bytearray = self.request.recv(msg_len)
                msg = msg_bytes.decode("utf-8")
                msg_sp = msg.split("\n")
                output = find(msg_sp)
                output = "".join(output)
                output_bytes = output.encode("utf-8")
                self.request.sendall(len(output_bytes).to_bytes(4, byteorder="big"))
                self.request.sendall(output_bytes)

        except Exception as e:
            pass
        finally:
            self.request.close()


def client():
    ip, port = "localhost", 9999
    with open("../in/test.txt", "r") as test_obj:
        msg = "".join(test_obj.readlines())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            msg_bytes = msg.encode("utf-8")
            msg_len = len(msg_bytes)
            sock.sendall(msg_len.to_bytes(4, byteorder="big"))
            sock.sendall(msg_bytes)
            response_len_bytes = sock.recv(4)
            response_len = int.from_bytes(response_len_bytes, byteorder="big")
            response_bytes = sock.recv(response_len)
            response = response_bytes.decode("utf-8")
            ##print(response)

        finally:
            sock.close()


def main():
    x = [0 for i in range(25)]
    y = [0 for i in range(25)]
    z = [0 for i in range(25)]
    num=0
    host, port = "localhost", 9999
    for ts in range(1, 6):
        for tc in range(1, 6):

            server = ThreadPoolTCPServer((host, port), MyTCPHandler)
            server.numThreads = ts
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            start = timeit.default_timer()
            for i in range(tc):
                client_thread = threading.Thread(target=client())
                client_thread.daemon = True
                client_thread.start()
            end = timeit.default_timer()
            find_time = end - start
            print("{0} {1} {2}".format(ts, tc, find_time*1000))
            x[num]=ts
            y[num]=tc
            z[num]=find_time*1000
            num=num+1
            server.shutdown()
            server_thread.join()
            server.server_close()
    # new a figure and set it into 3d
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # set figure information
    ax.set_title("3D_Curve")
    ax.set_xlabel("server")
    ax.set_ylabel("client")
    ax.set_zlabel("time")

    # draw the figure, the color is r = read
    figure = ax.plot(x,y,z, c='r')

    plt.show()


def find(words):
    with open("../out/sort.dat", "rb") as sort_obj:
        outputs = []
        for word in words:
            output = find_one(sort_obj, word.strip())
            if output is not None:
                outputs.append(output)
        return outputs


def find_one(sort_obj, word):
    size = os.fstat(sort_obj.fileno()).st_size
    block_num = int(size / 1024)
    output_next = False
    for block_index in range(0, block_num):
        block_local_index = 0
        sort_obj.seek(block_index * 1024)
        while block_local_index < 1024:
            t_len = sort_obj.read(1)
            if t_len == 0:
                break
            t = sort_obj.read(int.from_bytes(t_len, byteorder='big'))
            t_str = t.decode("utf-8")
            if output_next:
                return t_str + "\n"
            if word == t_str:
                output_next = True

            block_local_index = block_local_index + 1 + int.from_bytes(t_len, byteorder='big')

    return None


def store():
    words = set()
    with open("../in/sample.txt", "r") as sample_obj:
        for line in sample_obj:
            b = re.split(r'[^a-zA-Z_\']+', line)
            words |= set([w for w in b if len(w) > 0])
    words = list(words)
    words = sorted(words, key=str.lower)
    print(words)
    index = 0
    block_index = 0
    block = bytearray(1024)
    with open("../out/sort.dat", "wb") as sort_obj:
        while index < len(words):
            w = words[index]
            w_bytes = bytes(w, "utf-8")
            w_bytes_len = len(w_bytes)
            if w_bytes_len > 256:
                continue
            if block_index + 1 + w_bytes_len > 1024:
                sort_obj.write(block)
                block = bytearray(1024)
                block_index = 0
                pass
            else:
                block[block_index] = w_bytes_len
                block[block_index + 1:block_index + 1 + w_bytes_len] = w_bytes
                block_index = block_index + 1 + w_bytes_len
                index += 1
        if block_index != 0:
            sort_obj.write(block)


if __name__ == '__main__':
    main()
