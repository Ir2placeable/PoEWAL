from multiprocessing import Process
import threading
from queue import Queue
import os, sys, time
import socket


def connect_next():
    host = '127.0.0.1'
    port = 9997

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    client_socket, addr = server_socket.accept()

    print("Connected to next node")

    myqueue = Queue()
    send_thread = threading.Thread(target=send, args=(client_socket, myqueue))
    recv_thread = threading.Thread(target=recv, args=(client_socket, myqueue))

    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()


def send(client_socket, queue):
    while True:
        msg = queue.get()
        client_socket.send(msg.encode())


def recv(client_socket, queue):
    while True:
        msg = client_socket.recv(1024)
        print(msg.decode())


if __name__ == "__main__":
    prevqueue = Queue()
    # proc_for_prev = Process(target=connect_next, args=())
    # proc_for_prev.start()

    host = '127.0.0.1'
    port = 9998

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    send_thread = threading.Thread(target=send, args=(client_socket, prevqueue))
    recv_thread = threading.Thread(target=recv, args=(client_socket, prevqueue))

    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()

    # proc_for_prev.join()