import subprocess
import time
import csv
from pathlib import Path
from tabulate import tabulate   # pip install tabulate

# ---------------- CONFIG ----------------
interface = "wlan0"   # must already be in monitor mode
output_file = "capture"  # will create capture-01.csv, capture-02.csv, etc.
duration = 20  # seconds to run airodump
# ----------------------------------------


def run_airodump():
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

if __name__ == "__main__":
    run_airodump()

    # airodump names files like capture-01.csv, capture-02.csv...
    # Pick the newest one
    files = sorted(Path(".").glob(f"{output_file}-*.csv"), key=lambda f: f.stat().st_mtime)
    if not files:
        print("[!] No CSV file found.")
    else:
        latest_csv = files[-1]
        print(f"[+] Using results from {latest_csv}")
        display_tables(latest_csv)
