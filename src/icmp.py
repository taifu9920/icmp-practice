import select, struct, socket, sys, zlib

def get_checksum(packet):
    checksum = 0
    count = 0
    while count < len(packet):
        val = packet[count + 1]*256 + packet[count]                   
        checksum = (checksum + val) & 0xffffffff
        count += 2
    checksum = (checksum >> 16)  +  (checksum & 0xffff)
    checksum += (checksum >> 16)
    answer = ~checksum & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)

def receive(sock, size):
    timeout = 2
    try:
        pending = select.select([sock], [], [], timeout)
        if pending[0]:
            recv_packet, addr = sock.recvfrom(size)
            print("received packet size:",len(recv_packet))
            Type, code, checksum, ID, seq = struct.unpack("bbHHh", recv_packet[20:28])
            return Type, code, checksum, ID, seq, zlib.decompress(recv_packet[28:].rstrip(b"\x00")[:-4]), addr[0]
        return None
    except Exception as e:
        print(e) #Usually Network problem
        return None 
    
def send(target, ID = 0x1234, data = b"", Type=8):
    data = zlib.compress(data) + b"===="
    while len(data) < 18 or len(data) % 2 != 0: data += b"\0" # padding
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    header = struct.pack("bbHHh", Type, 0, 0, ID, 1)
    # htons() will convert decimal into network formatting
    # (BE & LE problem)
    checksum = socket.htons(get_checksum(header + data))
    header = struct.pack("bbHHh", Type, 0, checksum, ID, 1)
    packet = header + data
    print("sending packet size:",len(packet))
    sock.sendto(packet, (target, 1))
    return sock
    
def must_send(target, size, attempt_limit = 8, ID=0x1234, data=b"", Type=8, secondResult=False):
    conn = send(target, ID, data, Type)
    result = receive(conn, size)
    while attempt_limit > 0 and not result:
        result = receive(conn, size)
        attempt_limit -= 1
    if attempt_limit == 0 and not result:
        print("Failed to send ICMP!")
    else:
        print("Receive successful!")
        if secondResult: result = receive(conn, size)
        if result: print("Second result successful!")
        else: print("Second result failed")
    return result if attempt_limit > 0 and result else None