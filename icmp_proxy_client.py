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
            if data:
                send(target, ID, data)
            else: break
    except Exception as e:
        raise e

def icmp_forward(target, ID):
    #ICMP to TCP
    try:
        icmp = send(target, ID, b"")
        ping = receive(icmp, buffersize)
        while not ping: 
            icmp = send(target, ID, b"")
            ping = receive(icmp, buffersize)
        print("Ping successful")
        while status[0]:
            result = receive(icmp, buffersize)
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                print(ID, TCPs)
                if TCPs.get(ID):
                    try:
                        TCPs[ID].send(data)
                    except Exception as e:
                        TCPs[ID].close()
                        del TCPs[ID]
    except Exception as e:
        status[0] = False
        print("Error on ICMP forwarding!")
        raise e

def process(conn, ID, target):
    data = conn.recv(buffersize)
    method = data[:data.find(b" ")]
    if(method.lower() == b"connect"):
        try:
            threading.Thread(target=forward, args=(conn, target, addr[1]), daemon = True).start()
            threading.Thread(target=icmp_forward, args=(target,addr[1]), daemon = True).start()
            print("Trying to connect ICMP proxy server...")
            result = must_send(target, buffersize, 8, addr[1], data)
            if result: print("ICMP connect request sent")
            else: print("Failed to send icmp connect data")
        except Exception as e:
            del TCPs[addr[1]]
            conn.close()
            print("Forward connection failed")
    else:
        try:
            result = must_send(target, buffersize,8, addr[1], data, 8, True)
            Type, code, checksum, ID, seq, data, IP = result
            conn.send(result)
            if result: print("Web request successful")
            else: print("Web request failed")
        except Exception as e:
            conn.close()
            print("Request connection failed")
    

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