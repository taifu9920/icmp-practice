from src.icmp import *
import socket, threading
status = [True]
buffersize = 2**16

def recv(status):
    try:
        icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp.bind(("0.0.0.0", 0))
        while status[0]:
            result = receive(icmp, 1024) # fetch feedback
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                send(IP, ID, data, 0) # Echo reply
                data = data.decode("utf-8")
                print(data)
        icmp.close()
    except Exception as e:
        icmp.close()
        raise e

def main():
    try:
        print(f"Fetching ping...")
        threading.Thread(target=recv, args = (status,), daemon = True).start()

        while status[0]:
            cmd = input("Terminal# ").lower().strip()
            if cmd == "stop" or cmd == "exit":
                status[0] = False
            elif cmd == "help":
                print(" - Command Menu -")
                print("stop/exit - Stop and exit the server")
                print("help - Show this helpful menu")
        print("Server stopped")
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    main()