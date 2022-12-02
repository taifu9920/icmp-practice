import socket, threading, sys, ssl, zlib
from src.icmp import *

connection_limit = 5 # non-accepted connections limit
status = [True]
buffersize = 2**16

def forward(conn, target):
    #TCP to ICMP
    try:
        while status[0]:
            data = conn.recv(buffersize)
            if data:
                data = zlib.compress(data)
                proxy = send(target, 0x1234, data)
                result = receive(conn)
                while status[0] and result:
                    print("ICMP timeout, resending...")
                    proxy = send(target, 0x1234, data)
                    result = receive(conn)
            else: break
    except Exception as e:
        raise e

def icmp_forward(target, conn):#WIP
    #ICMP to TCP
    try:
        while status[0]:
            data = conn1.recv(buffersize)
            if data: conn2.send(data)
            else: break
    except Exception as e:
        raise e
        
def recv(status, sock, target):
    while status[0]:
        conn, addr = sock.accept()
        print("Received a connection from",addr)
        data = conn.recv(buffersize)
        method = data[:data.find(b" ")]
        if(method.lower() == b"connect"):
            try:
                threading.Thread(target=icmp_forward, args=(target, conn), daemon = True).start()
                threading.Thread(target=forward, args=(conn,target), daemon = True).start()
                conn.send(f"HTTP/{version} 200 Connection Established".encode())
                print("CONNECT method connection established")
            except Exception as e:
                conn.close()
                print("Forward connection failed")
        else:
            try:
                proxy = send(target, 0x1234, zlib.compress(data)) # send ping
                result = receive(conn) # fetch feedback
                if result:
                    Type, code, checksum, ID, seq, data = result
                    conn.send(zlib.decompress(data))
                conn.close()
                print("Web request successful and released")
            except Exception as e:
                conn.close()
                print("Request onnection failed")

def main():
    if len(sys.argv) < 3:
        print("Usage: proxy_server.py {The Port you wanted} {ICMP PROXY SERVER IP}")
    else:
        port = eval(sys.argv[1])
        target = eval(sys.argv[2])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        sock.listen(connection_limit)
        print(f"Server is listening on {port}")
        print("Waiting for connections...")
        receive = threading.Thread(target=recv, args = (status, sock, target), daemon = True)
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