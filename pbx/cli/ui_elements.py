# pbx/cli/ui_elements.py

import sys
import os
from pathlib import Path
from datetime import datetime
from .color_utils import color

# Path to consent file → parent of cli/
CONSENT_FILE = Path(__file__).resolve().parent.parent.parent / ".pbx_consent"

# Banner art
BANNER = r"""
    ____  _____  ____    ____  ___    ____     _  __
   / __ \/   \ \/ / /   / __ \/   |  / __ \   | |/ /
  / /_/ / /| |\  / /   / / / / /| | / / / /   |   / 
 / ____/ ___ |/ / /___/ /_/ / ___ |/ /_/ /   /   |  
/_/   /_/  |_/_/_____/\____/_/  |_/_____/   /_/|_|  

                [ PayloadBuilder X ] 

    ▸ Author: diputs-sudo
    ▸ Unauthorized use is illegal and YOUR responsibility
    ▸ Created for ethical red teaming, research, and education
"""

# Consent art
CONSENT_ART = color(r"""
╔═════════════════════════════════════════════════════════════════╗
║                        PAYLOADBUILDER X                         ║
║                     OFFENSIVE SECURITY TOOL                     ║
╠═════════════════════════════════════════════════════════════════╣
║ WARNING: This software is intended solely for educational,      ║
║ research, or authorized penetration testing purposes.           ║
║                                                                 ║
║ ▸ You must have explicit, written permission to run payloads.   ║
║ ▸ Unauthorized use on systems you do not own or control         ║
║   may violate local, state, federal, or international laws.     ║
║ ▸ The authors assume no liability for misuse or damage.         ║
║                                                                 ║
║ By continuing, you acknowledge that:                            ║
║ [1] You understand and accept the above risks.                  ║
║ [2] You are solely responsible for your actions.                ║
║                                                                 ║
║ To proceed, you must SIGN your name below.                      ║
╚═════════════════════════════════════════════════════════════════╝
""", "red")

def show_banner():
    print(BANNER)

def clear_terminal():
    try:
        if os.name == 'nt':  
            os.system('cls')
        else:
            os.system('clear')
    except Exception:
        print("[!] Failed to clear terminal.")

def get_signed_name():
    if CONSENT_FILE.exists():
        try:
            lines = CONSENT_FILE.read_text().splitlines()
            for line in lines:
                if line.startswith("Signed by:"):
                    return line.replace("Signed by:", "").strip()
        except Exception:
            pass
    return "user"

def show_welcome_message():
    signed_name = get_signed_name()
    print(color(f"\n+=== Welcome back {signed_name} ===+", "green"))

def show_hacker_consent():
    first_time = not CONSENT_FILE.exists()

    if not first_time:
        return  

    print(CONSENT_ART)

    if not sys.stdin.isatty():
        print("[!] Non-interactive execution detected.")
        print("    → For legal and ethical reasons, this tool must be run in an interactive shell.")
        sys.exit(1)

    try:
        while True:
            response = input("→ Do you acknowledge full legal responsibility and understand the risks? (yes/no): ").strip().lower()
            if response in {"yes", "y"}:
                break
            elif response in {"no", "n"}:
                print("✖ Consent not granted. Exiting.")
                sys.exit(1)
            else:
                print("Please type 'yes' or 'no'.")

        # Ask for signature
        print("\nPlease type your full name to sign the following agreement:\n")
        print("I understand I will only use PayloadBuilder X for ethical purposes")
        print("and accept full legal responsibility for its use.\n")

        while True:
            signature = input("Signed by: ").strip()
            if signature:
                break
            else:
                print("Please enter your name to proceed.")

        # Save consent file
        try:
            CONSENT_FILE.write_text(
                "I understand I will only use PayloadBuilder X for ethical purposes\n"
                "and accept full legal responsibility for its use.\n\n"
                f"Signed by: {signature}\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            print(f"\n✓ Consent saved in {CONSENT_FILE}.")
        except Exception as e:
            print(f"[!] Failed to save consent file: {e}")
            sys.exit(1)

        # Clear terminal after first time only
        input("\n→ Press Enter to continue...")
        clear_terminal()

    except KeyboardInterrupt:
        print("\n✖ Interrupted. Exiting.")
        sys.exit(1)
