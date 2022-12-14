import socket, threading, sys, ssl, time
from src.icmp import *

status = [True]
buffersize = 2**15
TCPs = dict()

def forward(conn, target, ID):
    #TCP to ICMP
    try:
        while status[0]:
            data = conn.recv(buffersize - 2**12)
            if len(data) > buffersize - 2**12:
                slices = [data[i:i+buffersize - 2**12] for i in range(0, len(data),buffersize - 2**12)]
                for i in slices:
                    send(target, ID, i, 0)
            elif data: send(target, ID, data, 0)
            else: break
    except Exception as e:
        raise e

def icmp_listener():
    #ICMP to TCP
    try:
        icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp.bind(("0.0.0.0", 0))
        while status[0]:
            result = receive(icmp, buffersize)
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                send(IP, ID, b"echoreply", 0) # echo reply
                if data:
                    if ID in TCPs: 
                        #print("sending", data, "to web request ID", ID)
                        try:
                            TCPs[ID].send(data)
                        except Exception:
                            print("Failed to send, socket is dead")
                            del TCPs[ID]
                    else:
                        try:
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
                            #print(hostname, port)
                            if hostname and port:
                                try:
                                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    server.connect((hostname, port))
                                    TCPs[ID] = server
                                    threading.Thread(target=forward, args=(server, IP, ID), daemon = True).start()
                                    if(method.lower() == b"connect"):
                                        send(IP, ID, f"HTTP/{version} 200 Connection established".encode(), 0)
                                    else: server.send(data)
                                except Exception as e:
                                    server.close()
                                    print("Forward connection failed")
                        except Exception as e:
                            print(data)
                            print("Can't read this packet!")
                            "I can't process this part for now"
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