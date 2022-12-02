from src.icmp import *

def main():
    icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp.bind(("0.0.0.0", 0))
    try:
        print(f"Fetching ping...")
        while 1:
            result = receive(icmp, 1024) # fetch feedback
            if result:
                Type, code, checksum, ID, seq, data, addr = result
                send(addr[0], ID, data, 0) # Echo reply
                data = data.decode("utf-8")
                print(data)
        icmp.close()
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    main()