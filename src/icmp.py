import select, struct, socket, sys

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
    pending = select.select([sock], [], [], timeout)
    if pending[0]:
        recv_packet, addr = sock.recvfrom(size)
        Type, code, checksum, ID, seq = struct.unpack("bbHHh", recv_packet[20:28])
        return Type, code, checksum, ID, seq, recv_packet[28:], addr[0]
    return None
    
def send(target, ID = 0x1234, data = b""):
    while len(data) < 18 or len(data) % 2 != 0: data += b" " # padding
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    header = struct.pack("bbHHh", 8, 0, 0, ID, 1)
    # htons() will convert decimal into network formatting
    # (BE & LE problem)
    checksum = socket.htons(get_checksum(header + data))
    header = struct.pack("bbHHh", 8, 0, checksum, ID, 1)
    packet = header + data
    sock.sendto(packet, (target, 1))
    return sock