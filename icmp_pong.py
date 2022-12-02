from src.icmp import *
import socket, threading
status = [True]
buffersize = 2**16
last = [None, None, None]

def recv(status, last):
    try:
        icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp.bind(("0.0.0.0", 0))
        while status[0]:
            result = receive(icmp, 1024) # fetch feedback
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                last[0], last[1], last[2] = IP, ID, data
                send(IP, ID, data, 0) # Echo reply
                data = data.decode("utf-8")
                print("received:",data)
            if last[0] != None: send(last[0], last[1], last[2], 8) # Echo reply
        icmp.close()
    except Exception as e:
        icmp.close()
        raise e

def main():
    try:
        print(f"Fetching ping...")
        threading.Thread(target=recv, args = (status,last), daemon = True).start()

        while status[0]:
            cmd = input("Terminal# ").lower().strip()
            if cmd == "stop" or cmd == "exit":
                status[0] = False
            elif cmd == "help":
                print(" - Command Menu -")
                print("stop/exit - Stop and exit the server")
                print("help - Show this helpful menu")
            elif last[0]:
                send(last[0], last[1], last[2], 0)
        print("Server stopped")
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    main()