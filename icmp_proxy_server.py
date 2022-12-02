import socket, threading, sys, ssl
from src.icmp import *

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
                proxy = mustsend(target, buffersize, 8, ID, data)
            else: break
    except Exception as e:
        raise e

def process(IP, data, ID):
    method = data[:data.find(b" ")]
    URL = data[data.find(b" ")+1:]
    version = data[data.find(b" ")+1:]
    version = version[version.find(b"HTTP/")+5:]
    version = version[:version.find(b"\r\n")]
    URL = URL[:URL.find(b" ")]
    if (URL.startswith(b"http")):
        hostname = URL[URL.find(b"://")+3:]
        hostname = hostname[:hostname.find(b"/")]
    else: 
        hostname = URL
    if hostname.find(b":") != -1:
        port = eval(hostname[hostname.find(b":")+1:])
        hostname = hostname[:hostname.find(b":")]
    elif URL.startswith(b"https://"): port = 443
    else: port = 80
    path = b"/"
    if hostname and port:
        if(method.lower() == b"connect"):
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.connect((hostname, port))
                threading.Thread(target=forward, args=(server, IP, ID), daemon = True).start()
                result = mustsend(IP, buffersize, 8, ID, f"HTTP/{version} 200 Connection Established".encode())
                if result: print("CONNECT method connection established")
            except Exception as e:
                server.close()
                print("Forward connection failed")
        else:
            if TCPs.get(ID): TCPs[ID].send(data)
            else:
                try:
                    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    proxy.connect((hostname, port))
                    proxy.send(data)
                    result = proxy.recv(buffersize)
                    if result: mustsend(IP, buffersize, 8, ID, result)
                    proxy.close()
                    print("Web request successful and released")
                except Exception as e:
                    proxy.close()
                    print("Request onnection failed")

def icmp_listener():
    #ICMP to TCP
    try:
        icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp.bind(("0.0.0.0", 0))
        while status[0]:
            result = receive(icmp, buffersize)
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                print(ID, data)
                send(IP, ID, data, 0) # echo reply
                threading.Thread(target=process, args=(IP, data, ID)).start()
    except Exception as e:
        status[0] = False
        print("Error on ICMP forwarding!")
        raise e

def main():
    print(f"Server is listening ICMP packet now")
    print("Waiting for connections...")
    #ICMP listener
    threading.Thread(target=icmp_listener, daemon = True).start()
    
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