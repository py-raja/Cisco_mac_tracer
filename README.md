# Cisco MAC Address Tracer
This script utilizes Netmiko to trace the MAC address for a given IP address across multiple Cisco switches. It iterates through a list of target IPs and follows the path through the network using CDP (Cisco Discovery Protocol).

## Features:

Connects to Cisco switches using Netmiko.
Uses ARP and MAC address tables to retrieve MAC address and connected port.
Handles trunk ports by extracting member interfaces and performing CDP on the first member.
Supports reading IP addresses and credentials from separate text files.
Provides informative output, including target IP, switch IP, and connected interface.
Includes basic error handling for Netmiko exceptions and unexpected errors.
## Requirements:
```
- Python 3
- Netmiko library (pip install netmiko)
- Cisco devices accessible via SSH
```
## Usage:

1.Install Netmiko:
```
pip install netmiko
```
2.Create Input File (input.txt):
- List one target IP address per line.
Example input.txt:
```
192.168.1.100
10.0.0.2
172.16.10.254
```
3.Create Credentials File (credentials.txt):
- On the first line, provide the username for switch access.
- On the second line, provide the password for switch access.
Example credentials.txt:
```
admin
cisco123
```
## Run the Script:
python l2tracer.py
The script will prompt you for the starting switch IP address.

### Example Output:
```
Enter Switch IP address: 192.168.1.1
IP Address: 10.0.0.10, Switch IP: 192.168.2.2, Switch Interface: Gi1/0/1
IP Address: 10.0.0.20, Switch IP: 192.168.3.3, Switch Interface: Fa0/0/1
MAC address for IP 10.0.0.30 not found.
```
### Notes:

- Ensure the input and credentials files are in the same directory as the script.
- Edit the file paths (input_file and credentials_file) in the script if needed.
- Remember to update switch IP addresses and credentials in the respective files.
- This script is a basic example and might require adjustments for specific network configurations.
### Further Development:

- Implement more sophisticated error handling for specific scenarios.
- Add functionality to handle different switch vendors (besides Cisco).
- Enhance output formatting for better readability.
- This script provides a starting point for automating MAC address tracing across your network. Feel free to modify and extend it based on your needs.
