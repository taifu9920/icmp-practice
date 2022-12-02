from src.icmp import *

default_target = "rmh.i234.me"

def main():
    if (len(sys.argv) < 2): target = [default_target]
    else: target = sys.argv[1:]
    for i in target:
        try:
            print(f"Pinging {i}...")
            conn = send(i, 0x1234, b"Hello world") # send ping
            result = receive(conn, 1024) # fetch feedback
            if result:
                Type, code, checksum, ID, seq, data, IP = result
                data = data.decode("utf-8")
                print(data)
            else: print("Timeout!")
            conn.close()
        except Exception as e:
            raise(e)

if __name__ == "__main__":
    main()