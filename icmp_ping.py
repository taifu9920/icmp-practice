from src.icmp import *
import socket, threading
default_target = "rmh.i234.me"

def main():
    status = True
    if (len(sys.argv) < 2): target = default_target
    else: target = sys.argv[1]
    while status:
        cmd = input("Terminal# ").lower().strip()
        if cmd == "stop" or cmd == "exit":
            status = False
        elif cmd == "help":
            print(" - Command Menu -")
            print("stop/exit - Stop and exit the server")
            print("help - Show this helpful menu")
        else:
            try:
                print(f"Pinging {target}...")
                conn = send(target, 0x1234, cmd.encode()) # send ping
                result = receive(conn, 1024) # fetch feedback
                if result: print("data sent!")
                else: print("Timeout!")
                conn.close()
            except Exception as e:
                raise(e)
    print("Server stopped")

if __name__ == "__main__":
    main()