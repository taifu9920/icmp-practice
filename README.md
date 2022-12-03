# ICMP project for CSC521
##### This Project can hides a proxy server behind ICMP
## How to Run:
##### 1. Run `python3 icmp_proxy_server.py` on the machine you want as proxy server host
##### 2. And the machine must have set to ignore Echo Reply
##### 3. (See this if you don't know how to
##### 4. https://unix.stackexchange.com/questions/412446/how-to-disable-ping-response-icmp-echo-in-linux-all-the-time)
##### 5. And run `python3 icmp_proxy_client.py {The port you liked} {The proxy server host IP}` on your laptop, It creates a service on local
##### 6. Then you need to connect to the port you gave to `icmp_proxy_client.py`
##### 7. (Here I use Firefox to debug)
##### 8. Fill in the proxy info on HTTP and HTTPS, with `localhost:{The port you liked}`
##### 9. Then you're all good, The proxy server should work now
## How it Works:
##### The document still WIP, sorry ;w;
