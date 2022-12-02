from socket import * 
icmp_listener_sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
icmp_listener_sock.bind(("0.0.0.0", 0))
print(icmp_listener_sock.recvfrom(2048))