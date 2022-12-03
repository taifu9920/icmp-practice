import socket, threading, sys, ssl, select

connection_limit = 5 # non-accepted connections limit
status = [True]
buffersize = 2**16

def forward(conn1, conn2):
    #TCP to TCP
    try:
        while status[0]:
            data = conn1.recv(buffersize)
            if data: conn2.send(data)
            else: break
    except Exception as e:
        raise e
    

def recv(status, sock):
    while status[0]:
        conn, addr = sock.accept()
        print("Received a connection from",addr)
        data = conn.recv(buffersize)
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
                    threading.Thread(target=forward, args=(conn,server), daemon = True).start()
                    threading.Thread(target=forward, args=(server,conn), daemon = True).start()
                    conn.send(f"HTTP/{version} 200 Connection Established".encode())
                    print("CONNECT method connection established")
                except Exception as e:
                    server.close()
                    conn.close()
                    print("Forward connection failed")
            else:
                try:
                    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    proxy.connect((hostname, port))
                    proxy.send(data)
                    while 1:
                        print("waiting for data")
                        pending = select.select([proxy], [], [], 5)
                        print("have data!")
                        if pending[0]: 
                            result = proxy.recv(buffersize)
                            print(result)
                            conn.send(result)
                        else: break
                    proxy.close()
                    conn.close()
                    print("Web request successful and released")
                except Exception as e:
                    proxy.close()
                    conn.close()
                    raise e
                    print("Request connection failed")

def main():
    if len(sys.argv) < 2:
        print("Usage: proxy_server.py {The Port you wanted}")
    else:
        port = eval(sys.argv[1])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        sock.listen(connection_limit)
        print(f"Server is listening on {port}")
        print("Waiting for connections...")
        receive = threading.Thread(target=recv, args = (status, sock), daemon = True)
        receive.start()
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