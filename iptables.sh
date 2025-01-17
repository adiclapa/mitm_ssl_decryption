#!/bin/bash

# Flush old rules (optional, use if testing)
sudo iptables -F
sudo iptables -t nat -F

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Mark HTTP/HTTPS traffic for redirection to redsocks (using PREROUTING)
iptables -t nat -A PREROUTING -i ens160 -p tcp --dport 80 -j REDIRECT --to-ports 12345
iptables -t nat -A PREROUTING -i ens160 -p tcp --dport 443 -j REDIRECT --to-ports 12345

# Forward all other traffic normally to default gateway
iptables -t nat -A POSTROUTING -o ens160 -j MASQUERADE

sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 127.0.0.1 --to-ports 12345

# sudo iptables -t nat -N REDSOCKS

# sudo iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
# sudo iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

# sudo iptables -t nat -A REDSOCKS -p tcp --dport 80 -j REDIRECT --to-ports 12345
# sudo iptables -t nat -A REDSOCKS -p tcp --dport 443 -j REDIRECT --to-ports 12345

# sudo iptables -t nat -A OUTPUT -p tcp -o ens160 -j REDSOCKS