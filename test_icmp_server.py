from socket import * 
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
sock.bind(("0.0.0.0", 0))
print(sock.recvfrom(2048)) #UDP receive