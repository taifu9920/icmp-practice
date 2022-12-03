import socket, threading, sys, ssl
from src.icmp import *

connection_limit = 5 # non-accepted connections limit
status = [True]
buffersize = 2**16
TCPs = dict()

def forward(conn, target, ID):
    #TCP to ICMP
    TCPs[ID] = conn
    try:
        while status[0]:
            data = conn.recv(buffersize)
            if data: must_send(target,buffersize, 8, ID, data)
            else: break
    except Exception as e:
        raise e

def icmp_forward(target, ID):
    #ICMP to TCP
    try:
        icmp = send(target, ID, b"")
        ping = receive(icmp, buffersize)
        while not ping: 
            print("Ping failed... retry!")
            icmp = send(target, ID, b"")
            ping = receive(icmp, buffersize)
        print("Ping successful")
        while status[0]:
            result = receive(icmp, buffersize)
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                if ID in TCPs:
                    try:
                        TCPs[ID].send(data)
                    except Exception as e:
                        TCPs[ID].close()
                        del TCPs[ID]
                        raise e
    except Exception as e:
        status[0] = False
        print("Error on ICMP forwarding!")
        raise e

def process(conn, ID, target):
    data = conn.recv(buffersize)
    method = data[:data.find(b" ")]
    if(method.lower() == b"connect"):
        try:
            threading.Thread(target=forward, args=(conn, target, ID), daemon = True).start()
            threading.Thread(target=icmp_forward, args=(target,ID), daemon = True).start()
            print("Trying to connect ICMP proxy server...")
            result = must_send(target, buffersize, 8, ID, data)
            if result: print("ICMP connect request sent")
            else: print("Failed to send icmp connect data")
        except Exception as e:
            if ID in TCPs: del TCPs[ID]
            conn.close()
            print("Forward connection failed")
    else:
        try:
            result = must_send(target, buffersize,8, ID, data, 8, True)
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                conn.send(data)
                #print("Web request successful")
            else:
                #print("Web request failed")
                conn.close()
        except Exception as e:
            conn.close()
            #print("Request connection failed")
            raise e
    

def recv(status, sock, target):
    #capture TCP and forward to ICMP
    while status[0]:
        conn, addr = sock.accept()
        print("Received a connection from",addr)
        threading.Thread(target=process, args=(conn, addr[1], target), daemon=True).start()

def main():
    if len(sys.argv) < 3:
        print("Usage: icmp_proxy_client.py {Local proxy server port} {ICMP proxy server IP}")
    else:
        port = eval(sys.argv[1])
        target = sys.argv[2]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        sock.listen(connection_limit)
        print(f"Server is listening on {port}")
        print("Waiting for connections...")
        threading.Thread(target=recv, args = (status, sock, target), daemon = True).start()

        while status[0]:
            cmd = input("Terminal# ").lower().strip()
            if cmd == "stop" or cmd == "exit":
                status[0] = False
            elif cmd == "help":
                print(" - Command Menu -")
                print("stop/exit - Stop and exit the server")
                print("help - Show this helpful menu")
            else:
                print("Unknown command, Use `help` to show all commands")
        print("Server stopped")

if __name__ == "__main__":
    main()