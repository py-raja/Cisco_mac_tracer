import netmiko
import re
import traceback
import argparse
import os


def find_mac_address(switch_ip, username, password, target_ip, mac_address):
    """
    Finds the MAC address for a given IP or uses the given MAC address to trace the switch port.

    Args:
        switch_ip: The IP address of the starting switch.
        username: The username for switch access.
        password: The password for switch access.
        target_ip: The target IP address to find the MAC address (optional if mac_address is provided).
        mac_address: The MAC address to trace (optional if target_ip is provided).

    Returns:
        The target IP (if provided), MAC address, switch address, and switch port, or None if not found.
    """

    next_switch_ip = None
    visited_switches = set()  # Track visited switches to avoid loops

    while switch_ip is not None and switch_ip not in visited_switches:
        visited_switches.add(switch_ip)

        try:
            # Connect to the switch using Netmiko
            device = netmiko.ConnectHandler(
                device_type="cisco_ios",
                ip=switch_ip,
                username=username,
                password=password,
            )

            # If MAC address is not provided, use ARP to find it
            if mac_address is None and target_ip is not None:
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
                    return target_ip, mac_address, switch_ip, connected_port
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
    with open(file_path, "r") as file:
        username = file.readline().strip()  # Read the first line for username
        password = file.readline().strip()  # Read the second line for password
    return username, password

def convert_to_cisco_format(mac_address):
  """Converts a MAC address to Period-separated Hexadecimal notation and removes whitespace.

  Args:
    mac_address: The MAC address to convert.

  Returns:
    The MAC address in Period-separated Hexadecimal notation with whitespace removed.
  """

  # Remove hyphens, colons, and whitespace
  mac_address = mac_address.replace("-", "").replace(":", "").replace(".", "").replace(" ", "")

  # Insert periods every two characters
  mac_address = ".".join([mac_address[i:i+4] for i in range(0, len(mac_address), 4)])

  return mac_address
  
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace MAC address across switches.")
    parser.add_argument("-m", "--mac", help="MAC address to trace.")
    parser.add_argument("-i", "--ip", help="IP address to find the MAC address.")
    parser.add_argument("-s", "--switch", help="Starting switch IP address.")
    parser.add_argument("-c", "--credentials", default="credentials.txt", help="Path to the credentials file.")
    parser.add_argument("-f", "--file", default="input.txt", help="File containing target IPs.")

    args = parser.parse_args()

    # Read username and password from the credentials file
    username, password = read_credentials(args.credentials)
    
    # File containing the IP addresses and credentials
    input_file = "input.txt"  # Change this path to your input file
    credentials_file = "credentials.txt"  # Change this path to your credentials file
    if args.switch is None:
        switch_ip = input("Enter Switch IP address: ")
    else:
        switch_ip = args.switch
    # If MAC address is provided, prioritize it over IP
    if args.mac:
        mac_address = convert_to_cisco_format(args.mac)
        result = find_mac_address(switch_ip, username, password, target_ip=None, mac_address=mac_address)
        if result is not None:
            print(f"MAC Address: {result[1]}, Switch IP: {result[2]}, Switch Interface: {result[3]}")
        else:
            print(f"MAC address {args.mac} not found.")
    elif args.ip:
        result = find_mac_address(switch_ip, username, password, target_ip=args.ip,mac_address=None)
        if result is not None:
            print(f"IP Address: {result[0]}, MAC Address: {result[1]}, Switch IP: {result[2]}, Switch Interface: {result[3]}")
        else:
            print(f"MAC address for IP {args.ip} not found.")
    elif os.path.exists("input.txt"):
        ip_addrs = read_input_file(input_file)
        for target_ip in ip_addrs:
            result = find_mac_address(switch_ip, username, password, target_ip,mac_address=None)
            if result is not None:
                print(f"IP Address: {result[0]}, Mac Address: {result[1]}, Switch IP: {result[2]}, Switch Interface: {result[3]}")
            else:
                print(f"MAC address for IP {target_ip} not found.")
