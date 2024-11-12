import netmiko
import re
import traceback

def find_mac_address(switch_ip, username, password, target_ip):
    """
    Finds the MAC address for a given IP address across multiple Cisco switches using Netmiko.
    
    Args:
        switch_ip: The IP address of the starting switch.
        username: The username for switch access.
        password: The password for switch access.
        target_ip: The target IP address for which to trace the MAC address pull the details from input.txt.

    Returns:
        The final target IP, switch address and switch port, or None if not found.
    """
    
    next_switch_ip = None
    mac_address = None
    visited_switches = set()  # Track visited switches to avoid loops

    while switch_ip is not None and switch_ip not in visited_switches:
        visited_switches.add(switch_ip)

        try:
            # Connect to the switch using Netmiko
            device = netmiko.ConnectHandler(
                device_type='cisco_ios',
                ip=switch_ip,
                username=username,
                password=password,
            )

            # If MAC address is not yet found (first switch), use ARP to find it
            if mac_address is None:
                # Find MAC address using ARP
                arp_output = device.send_command(f"show ip arp {target_ip}")

                # Extract MAC address from ARP output
                mac_match = re.search(r"([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})", arp_output)
                if mac_match:
                    mac_address = mac_match.group(1)
                else:
                    return None

            # Now that we have the MAC address, find the connected port
            mac_table_output = device.send_command(f"show mac address-table address {mac_address}")

            # Extract connected port from MAC address table output
            port_match = re.search(r"\s+(\d+)\s+([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+\S+\s+(\S+)", mac_table_output)
            if port_match:
                connected_port = port_match.group(3)

                # Check if the port is a trunk port
                config_output = device.send_command(f"show running-config interface {connected_port}")
                if "switchport mode trunk" in config_output:
                    # Step 4: Extract member interfaces from "show interfaces {port}" command
                    interfaces_output = device.send_command(f"show interfaces {connected_port}")

                    # Extract member interfaces (e.g., Gi1/2/0/13 Gi2/2/0/13)
                    members_match = re.search(r"Members in this channel: (.+)", interfaces_output)
                    if members_match:
                        member_interfaces = members_match.group(1)

                        # Step 5: Use the first member interface for CDP
                        first_member_interface = member_interfaces.split()[0]

                        # Find CDP neighbor information for the connected port
                        cdp_output = device.send_command(f"show cdp neighbors {first_member_interface} detail")

                        # Extract next switch IP from CDP neighbor details
                        cdp_match = re.search(r"IP address: ([0-9.]+)", cdp_output)
                        if cdp_match:
                            next_switch_ip = cdp_match.group(1)
                            switch_ip = next_switch_ip  # Set to the next switch to continue the loop
                        else:
                            return mac_address, connected_port
                    else:
                        # Step 5: Use the trunk interface for CDP
                        cdp_output = device.send_command(f"show cdp neighbors {connected_port} detail")

                        # Extract next switch IP from CDP neighbor details
                        cdp_match = re.search(r"IP address: ([0-9.]+)", cdp_output)
                        if cdp_match:
                            next_switch_ip = cdp_match.group(1)
                            switch_ip = next_switch_ip  # Set to the next switch to continue the loop
                        else:
                            return mac_address, connected_port

                else:
                    # Reached the end point (access port)
                    return target_ip, switch_ip, connected_port
            else:
                return None

        except netmiko.NetmikoTimeoutException as e:
            pass
        except netmiko.NetmikoAuthenticationException as e:
            pass
        except Exception as e:
            traceback.print_exc()  # Print detailed traceback for unexpected errors
        finally:
            try:
                device.disconnect()
            except:
                pass

        # If no next switch is found, end the loop
        if next_switch_ip is None:
            break

    return None

# Read input from a text file
def read_input_file(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and strip whitespace
        ip_addrs = [line.strip() for line in file if line.strip()]
        return ip_addrs

def read_credentials(file_path):
    with open(file_path, 'r') as file:
        username = file.readline().strip()  # Read the first line for username
        password = file.readline().strip()  # Read the second line for password
    return username, password

# File containing the IP addresses and credentials
input_file = "input.txt"  # Change this path to your input file
credentials_file = "credentials.txt"  # Change this path to your credentials file

# Read IP addresses from the file
ip_addrs = read_input_file(input_file)

# Read username and password from the credentials file
username, password = read_credentials(credentials_file)

switch_ip = input("Enter Switch IP address: ")  
for target_ip in ip_addrs:
    # Call the function 
    result = find_mac_address(switch_ip, username, password, target_ip)
    if result is not None:
        print(f"IP Address: {result[0]}, Switch IP: {result[1]}, Switch Interface: {result[2]}")
    else:
        print(f"MAC address for IP {target_ip} not found.")
