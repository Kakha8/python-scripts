import subprocess
import sys


#
def get_interface_mode(interface):
    try:
        output = subprocess.check_output(
            ["iw", "dev", interface, "info"],
            stderr=subprocess.DEVNULL
        ).decode()

        for line in output.splitlines():
            if "type" in line:
                return line.strip().split()[-1]
    except subprocess.CalledProcessError:
        return None

def list_wireless_interfaces():
    try:
        output = subprocess.check_output(["iw", "dev"]).decode()
        interfaces = []
        for line in output.splitlines():
            if "Interface" in line:
                interfaces.append(line.strip().split()[-1])

        return interfaces
    except subprocess.CalledProcessError:
        return []

def interfaces_by_mode(interfaces):
    ints = []
    i = 1
    for interface in interfaces:
        mode = get_interface_mode(interface)
        #print(interface + " is in" + get_interface_mode(interface))
        ints.append({'number':str(i), 'interface':interface, 'mode':mode})
        i = i + 1

    return ints

def list_by_mode(ints):

    try:
        print("\nList of wireless network interfaces:")
        i = 0

        for interface in ints:
            num = ints[i]['number']
            wlan = ints[i]['interface']
            mode = ints[i]['mode']
            print(num + ") "
                  + wlan + " ("
                  + mode + ")")
            i = i + 1

        selection = input("\nSelect interface that you want to set to Monitor Mode: ")
        i = 0
        for interface in ints:
            if ints[i]['number'] == selection:
                answer = input("Are you sure? (y/n): ")
                if answer == "Y" or "y":
                    set_monitor_mode(ints[i]['interface'])
                else:
                    list_by_mode()

    except KeyboardInterrupt:
        print("\nExiting...\n")
        sys.exit()

#def select_interface(interfaces):


def set_monitor_mode(interface_name):
    #iw = IW()
    try:

        # Bring the interface down
        subprocess.run(["ip", "link", "set", interface_name, "down"], check=True)

        # Change the mode to monitor
        #iw.set_interface(interface_name, iftype=NL80211_IFTYPE_MONITOR)

        subprocess.run(["iw", interface_name, "set", "type", "monitor"], check=True)

        # Bring the interface up
        subprocess.run(["ip", "link", "set", interface_name, "up"], check=True)

        print(f"Interface '{interface_name}' set to MONITOR mode.")

        menu()
    except Exception as e:
        print(f"Failed to set monitor mode on '{interface_name}': {e}")

def menu():

    # set_monitor_mode("wlan0")
    interfaces = list_wireless_interfaces()
    # print(get_interface_mode(interfaces[0]))
    ints = interfaces_by_mode(interfaces)
    list_by_mode(ints)
    # print(ints[0]['number'])



if __name__ == "__main__":

    menu()