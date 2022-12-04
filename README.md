# ICMP project for CSC521
##### This Project can hides a proxy server behind ICMP
##### The program may still having some problem, but it's able to use now
## How to Run:
##### 1. Run `python3 icmp_proxy_server.py` on the machine you want as proxy server host
##### 2. And the machine must have set to ignore Echo Reply (See this if you don't know how to https://unix.stackexchange.com/questions/412446/how-to-disable-ping-response-icmp-echo-in-linux-all-the-time)
##### 3. And run `python3 icmp_proxy_client.py {The port you liked} {The proxy server host IP}` on your laptop, It creates a service on local
##### 4. Then you need to connect to the port you gave to `icmp_proxy_client.py` (Here I use Firefox to debug, Windows's proxy setting doesn't seems to be working for now)
##### 5. Fill in the proxy info on HTTP and HTTPS, with `localhost:{The port you liked}`
##### 6. Then you're all good, The proxy server should work now
## How it Works:
##### The framework look like below, 
![image](https://github.com/taifu9920/icmp-practice/blob/main/Framework.png?raw=true)
##### The main goal on this project is to establish the connection between TCP and ICMP,
##### So any service can hides inside ICMP, like the demo are Proxy Server.
## Demo:
![image](https://github.com/taifu9920/icmp-practice/blob/main/demo/demo1.gif?raw=true)