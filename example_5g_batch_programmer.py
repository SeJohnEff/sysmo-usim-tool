#!/usr/bin/env python3
"""
Example: Production 5G SIM Card Batch Programming
For sysmoISIM-SJA5-9FV cards on private 5G SA networks

This is a REFERENCE IMPLEMENTATION showing how to use pySim for
advanced 5G SUCI programming when the GUI's built-in support is insufficient.

Requirements:
- pySim (https://github.com/osmocom/pysim)
- sysmo-usim-tool (this repository)
- HID OMNIKEY 3121 or compatible PCSC reader

Usage:
  1. Install pySim: git clone https://github.com/osmocom/pysim.git
  2. Create CSV with columns: imsi,ki,opc,adm1_pin,routing_indicator,
     protection_scheme_id,hnet_pubkey_identifier,hnet_pubkey
  3. Run: python3 example_5g_batch_programmer.py sim_data.csv

Credit: Based on production deployment script
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

# Tool paths (adjust if needed)
PYSIM_SHELL = "/opt/pysim/pySim-shell.py"  # Adjust to your pySim installation
SYSMO_TOOL = "./sysmo-isim-tool.sja5.py"   # In this repository

class SIMProgrammer:
    def __init__(self, pcsc_reader=0):
        self.pcsc_reader = pcsc_reader

    def run_command(self, cmd, check=True):
        """Execute shell command and return output."""
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\nError: {result.stderr}")
        return result.stdout

    def program_k_opc_imsi(self, adm1_pin, ki, opc, imsi):
        """
        Program K, OPc, and IMSI using sysmo-isim-tool.sja5.py
        This tool writes to all applications (SIM, USIM, ISIM) atomically.
        """
        print(f"  [1/4] Programming K, OPc, IMSI via sysmo-isim-tool...")

        # Program K
        cmd_k = f"{SYSMO_TOOL} -p {self.pcsc_reader} --adm1 {adm1_pin} -K {ki}"
        self.run_command(cmd_k)

        # Program OPc
        cmd_opc = f"{SYSMO_TOOL} -p {self.pcsc_reader} --adm1 {adm1_pin} -C {opc}"
        self.run_command(cmd_opc)

        # Program IMSI using pySim (sysmo-tool doesn't support IMSI)
        imsi_json = json.dumps({"imsi": imsi})
        pysim_script = f"""verify_adm {adm1_pin}
select MF/ADF.USIM/EF.IMSI
update_binary_decoded '{imsi_json}'
"""
        with open("/tmp/pysim_script.txt", "w") as f:
            f.write(pysim_script)

        cmd_imsi = f"{PYSIM_SHELL} -p {self.pcsc_reader} --script /tmp/pysim_script.txt"
        self.run_command(cmd_imsi)

    def program_5g_suci(self, adm1_pin, routing_indicator, prot_scheme_id,
                        hnet_pubkey_id, hnet_pubkey):
        """
        Program 5G SUCI parameters using pySim:
        - EF.SUCI_Calc_Info (protection scheme list + public keys)
        - EF.Routing_Indicator
        - Enable UST service 124 (SUCI by ME)
        - Disable UST service 125 (SUCI by USIM - not supported on 9FV variant)
        """
        print(f"  [2/4] Programming 5G SUCI parameters via pySim...")

        # Build SUCI_Calc_Info JSON structure
        suci_json = {
            "prot_scheme_id_list": [
                {"priority": 0, "identifier": int(prot_scheme_id), "key_index": 1}
            ],
            "hnet_pubkey_list": [
                {
                    "hnet_pubkey_identifier": int(hnet_pubkey_id),
                    "hnet_pubkey": hnet_pubkey.upper()
                }
            ]
        }

        # Convert to single-line JSON (pySim requirement)
        suci_json_str = json.dumps(suci_json).replace('"', '\\"')

        pysim_script = f"""verify_adm {adm1_pin}
select ADF.USIM/DF.5GS/EF.SUCI_Calc_Info
update_binary_decoded "{suci_json_str}"
select ADF.USIM/DF.5GS/EF.Routing_Indicator
update_binary {routing_indicator}ffffff
select ADF.USIM/EF.UST
ust_service_activate 124
ust_service_deactivate 125
"""
        with open("/tmp/pysim_5g.txt", "w") as f:
            f.write(pysim_script)

        cmd = f"{PYSIM_SHELL} -p {self.pcsc_reader} --script /tmp/pysim_5g.txt"
        self.run_command(cmd)

    def verify_programming(self, imsi):
        """Read back and verify key parameters."""
        print(f"  [3/4] Verifying programming via pySim...")

        pysim_script = f"""select ADF.USIM/EF.IMSI
read_binary_decoded
select ADF.USIM/DF.5GS/EF.SUCI_Calc_Info
read_binary_decoded
select ADF.USIM/EF.UST
read_binary_decoded
"""
        with open("/tmp/pysim_verify.txt", "w") as f:
            f.write(pysim_script)

        cmd = f"{PYSIM_SHELL} -p {self.pcsc_reader} --script /tmp/pysim_verify.txt"
        output = self.run_command(cmd, check=False)

        if imsi in output and "hnet_pubkey_list" in output:
            print(f"  [4/4] ✓ Verification PASSED")
            return True
        else:
            print(f"  [4/4] ✗ Verification FAILED")
            print(output)
            return False

    def program_one_sim(self, row):
        """Program a single SIM card from CSV row."""
        imsi = row["imsi"].strip()
        ki = row["ki"].strip().upper()
        opc = row["opc"].strip().upper()
        adm1_pin = row["adm1_pin"].strip()
        routing_indicator = row["routing_indicator"].strip()
        prot_scheme = row["protection_scheme_id"].strip()
        pubkey_id = row["hnet_pubkey_identifier"].strip()
        pubkey = row["hnet_pubkey"].strip()

        print(f"\n{'='*60}")
        print(f"Programming SIM: IMSI {imsi}")
        print(f"{'='*60}")

        try:
            # Step 1: Program authentication credentials
            self.program_k_opc_imsi(adm1_pin, ki, opc, imsi)

            # Step 2: Program 5G SUCI configuration
            self.program_5g_suci(adm1_pin, routing_indicator, prot_scheme,
                                pubkey_id, pubkey)

            # Step 3: Verify
            success = self.verify_programming(imsi)

            if success:
                print(f"\n✓ SUCCESS: Card IMSI {imsi} programmed successfully!")
                return True
            else:
                print(f"\n✗ FAILED: Card IMSI {imsi} verification failed!")
                return False

        except Exception as e:
            print(f"\n✗ ERROR programming card: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <sim_data.csv> [pcsc_reader_index]")
        print(f"\nExample: {sys.argv[0]} sim_data.csv 0")
        print(f"\nCSV Format: imsi,ki,opc,adm1_pin,routing_indicator,protection_scheme_id,hnet_pubkey_identifier,hnet_pubkey")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    pcsc_reader = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    programmer = SIMProgrammer(pcsc_reader=pcsc_reader)

    print("\n" + "="*60)
    print("sysmoISIM-SJA5 5G Batch Programming Tool (pySim Method)")
    print("="*60)

    successes = 0
    failures = 0

    with csv_path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total = len(rows)

        print(f"\nFound {total} cards to program")

        for idx, row in enumerate(rows, 1):
            input(f"\n[{idx}/{total}] Insert SIM for IMSI {row['imsi']} and press ENTER...")

            if programmer.program_one_sim(row):
                successes += 1
            else:
                failures += 1
                response = input("\nContinue to next card? (y/n): ")
                if response.lower() != 'y':
                    break

    print("\n" + "="*60)
    print(f"Batch Programming Complete")
    print(f"  Successful: {successes}/{total}")
    print(f"  Failed:     {failures}/{total}")
    print("="*60)

if __name__ == "__main__":
    main()
