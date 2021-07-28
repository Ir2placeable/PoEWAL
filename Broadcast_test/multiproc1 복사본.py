import multiprocessing
import threading
from queue import Queue
import os, sys, time
import socket

def send(client_socket, queue):
    while True:
        msg = queue.get()
        client_socket.send(msg.encode())

def recv(client_socket, queue):
    while True:
        msg = client_socket.recv(1024)
        print(msg.decode())

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    client_socket, addr = server_socket.accept()

    print("Connected to next node")

    queue = Queue()

    send_thread = threading.Thread(target=send, args=(client_socket, queue))
    recv_thread = threading.Thread(target=recv, args=(client_socket, queue))

    send_thread.start()
    recv_thread.start()

    while True:
        print("input : ")
        msg = input()
        queue.put(msg)

    send_thread.join()
    recv_thread.join()