import socket, threading, sys

connection_limit = 5
status = [True]
buffersize = 2**16

def proxy(status, conn, addr):
    data = conn.recv(buffersize)
    print(data)
    while status[0]:
        "WIP"

def recv(status, sock):
    while status[0]:
        conn, addr = sock.accept()
        thread = threading.Thread(target=proxy, args=(status,conn, addr), daemon=True)
        thread.start()

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