# Cisco MAC Address Tracer
This updated script utilizes Netmiko to trace the MAC address or IP address across multiple Cisco switches. It provides flexible tracing options by allowing you to specify either a MAC address or an IP address and tracks the switch path through the network using CDP (Cisco Discovery Protocol).

## Features:

- Connects to Cisco switches using Netmiko.
- Supports both MAC address tracing and IP address to MAC address resolution.
- Handles trunk ports by extracting member interfaces and performing CDP on the first member.
- Allows command-line arguments for flexibility.
- Reads IP addresses and credentials from separate text files.
- Provides detailed output, including target IP, MAC address, switch IP, and connected interface.
- Includes error handling for Netmiko exceptions and unexpected errors.

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
python l2tracer.py -s <starting_switch_ip> [-m <mac_address>] [-i <ip_address>] [-c <credentials_file>] [-f <input_file>]

###Command-Line Options:

-s or --switch: Specify the starting switch IP address (required).
-m or --mac: Specify the MAC address to trace (optional if -i is provided).
-i or --ip: Specify the target IP address to resolve to a MAC address (optional if -m is provided).
-c or --credentials: Specify the path to the credentials file (default: credentials.txt).
-f or --file: Specify the path to the input file containing target IPs (default: input.txt).

### Example Commands:
1.Trace a MAC address:
```
python l2tracer.py -s 192.168.1.1 -m 00:1A:2B:3C:4D:5E
```
2.Trace an IP address:
```
python l2tracer.py -s 192.168.1.1 -i 192.168.10.20
```
3.Trace IPs listed in a file:
```
python l2tracer.py -s 192.168.1.1
```

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
- Use the -c and -f arguments to specify alternate file paths if necessary.
- Edit the file paths (input_file and credentials_file) in the script if needed.
- Remember to update switch IP addresses and credentials in the respective files.
- This script is a basic example and might require adjustments for specific network configurations.
### Improvements in This Version:

- Added support for command-line arguments.
- Introduced MAC address input and conversion to Cisco format.
- Enhanced flexibility by allowing either a MAC address or an IP address to be traced.
- Improved error handling and input validation.

### Further Development:

- Implement more sophisticated error handling for specific scenarios.
- Add functionality to handle different switch vendors (besides Cisco).
- Enhance output formatting for better readability.
- This script provides a starting point for automating MAC address tracing across your network. Feel free to modify and extend it based on your needs.
