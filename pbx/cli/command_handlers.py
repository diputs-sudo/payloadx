# pbx/cli/command_handlers.py

import os
import json
import re
import difflib
import time
from datetime import datetime
from pathlib import Path
from .config import PAYLOAD_PROFILE, BUILTIN_CMDS, VERSION
from .color_utils import color
# from builder.compiler import compile_payload

# Global toggle for history recording
HISTORY_ENABLED = True

# Paths
CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"
HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"
HISTORY_FILE = HISTORY_DIR / "history.log"

# Ensure directories exist
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# Utility functions
def typo_match(word, candidates):
    word = word.lower()
    matches = difflib.get_close_matches(word, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None

def validate_config(cfg):
    errors = []
    if "port" in cfg:
        try:
            port = int(cfg["port"])
            if not (1 <= port <= 65535):
                errors.append("port must be between 1 and 65535.")
        except ValueError:
            errors.append("port must be a valid integer.")
    if "ip" in cfg:
        host = cfg["ip"]
        ipv4 = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        ipv6 = re.compile(r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$")
        if not (ipv4.match(host) or ipv6.match(host)):
            errors.append("ip must be a valid IPv4 or IPv6 address.")
    return errors

# Handlers
def handle_list(cfg):
    pt = cfg.get("payload_type")
    display_pt = pt if pt else "<none>"

    from .config import OPTIONS_INFO

    if not pt:
        # When payload_type not set → show hint
        print(f"\n--- Payload Type: " + color(display_pt, "cyan") + " ---\n")
        print("Current configuration (* required)")
        print(f"{'Options'.ljust(20)}| Value")
        print(f"{'-'*20}+{'-'*30}")
        print(f"[*] please set a payload_type")
        print("    → Use: set payload_type VALUE\n")
        return

    profile = PAYLOAD_PROFILE.get(pt)
    if not profile:
        print(color(f"[!] Unknown payload_type '{pt}'.", "red"))
        return

    required = profile["required"]
    optional = profile["optional"]
    defaults = profile["defaults"]

    rows = []

    # Required first
    for key in required:
        val = cfg.get(key, "")
        row = (f"* {key}", val)
        rows.append(row)

    # Optional next
    for key in optional:
        val = cfg.get(key, defaults.get(key, ""))
        row = (f"  {key}", val)
        rows.append(row)

    # Print header
    print(f"\n--- Payload Type: " + color(display_pt, "cyan") + " ---\n")

    # Print table
    col = max(len(left) for left, _ in rows) + 2
    print("Current configuration (* required)")
    print(f"{'Options'.ljust(col)}| Value")
    print(f"{'-'*col}+{'-'*30}")
    for left, right in rows:
        if left.startswith("*"):
            star = "* "
            option_name = left[2:]
        else:
            star = "  "
            option_name = left.strip()

        print(f"{star}" + color(f"{option_name.ljust(col - len(star))}", "cyan") + f"| {right}")
    print()

def handle_scan(arg):
    tokens = arg.strip().split()
    if not tokens:
        print("[!] Usage: scan [blocks|addons|plugins]")
        return
    target = tokens[0].lower()
    print(f"[*] Scanning for {target} ... (backend not implemented yet)\n")

def handle_config(cfg, arg):
    tokens = arg.strip().split()
    if not tokens:
        print("[!] Usage: config save NAME | config load NAME")
        return
    action = tokens[0].lower()
    if action == "save" and len(tokens) == 2:
        name = tokens[1]
        path = CONFIGS_DIR / f"{name}.json"
        try:
            with path.open("w") as f:
                json.dump(cfg, f, indent=2)
            print(f"✓ Config saved to {path}.")
        except Exception as e:
            print(f"[!] Failed to save config: {e}")
    elif action == "load" and len(tokens) == 2:
        name = tokens[1]
        path = CONFIGS_DIR / f"{name}.json"
        if not path.exists():
            print(f"[!] Config '{name}' not found.")
            return
        try:
            loaded = json.load(path.open())
            cfg.clear()
            cfg.update(loaded)
            print(f"✓ Config '{name}' loaded.")
        except Exception as e:
            print(f"[!] Failed to load config: {e}")
    else:
        print("[!] Usage: config save NAME | config load NAME")

def handle_wizard(cfg):
    print("[*] Wizard not implemented yet.\n")

def handle_history(cfg, args):
    from .color_utils import color
    path = Path(__file__).resolve().parent.parent / "history" / "history.log"
    if not path.exists():
        print(color("[!] No history found.", "red"))
        return

    lines = path.read_text().splitlines()
    if not lines:
        print(color("[!] No history entries.", "red"))
        return

    tokens = args.strip().split()

    # Default → show last 10 entries
    if not tokens or tokens[0] == "all":
        to_show = lines if tokens and tokens[0] == "all" else lines[-10:]
        print(color(f"\n[History] Showing {len(to_show)} entries:\n", "cyan"))
        for line in to_show:
            _print_history_line(line)
        return

    if tokens[0] == "clear":
        confirm = input(color("[?] Are you sure you want to clear history? (yes/no): ", "yellow")).strip().lower()
        if confirm in {"yes", "y"}:
            path.write_text("")
            print(color("[✓] History cleared.", "green"))
        else:
            print(color("[!] Clear cancelled.", "red"))
        return

    if tokens[0] == "show":
        if len(tokens) < 3:
            print(color("[!] Usage: history show top/bottom N", "red"))
            return
        which, n_str = tokens[1], tokens[2]
        try:
            n = int(n_str)
        except ValueError:
            print(color("[!] Invalid number.", "red"))
            return
        if which == "top":
            to_show = lines[:n]
        elif which == "bottom":
            to_show = lines[-n:]
        else:
            print(color("[!] Usage: history show top/bottom N", "red"))
            return
        print(color(f"\n[History] Showing {which} {n} entries:\n", "cyan"))
        for line in to_show:
            _print_history_line(line)
        return

    if tokens[0] == "find":
        if len(tokens) < 3:
            print(color("[!] Usage: history find <key> <value>", "red"))
            return
        key, value = tokens[1], tokens[2]
        print(color(f"\n[History] Searching for {key}={value}:\n", "cyan"))
        found = False
        for line in lines:
            if f"{key}={value}" in line:
                _print_history_line(line, highlight=True, match=f"{key}={value}")
                found = True
        if not found:
            print(color("[!] No matching history entries found.", "red"))
        return

    print(color("[!] Unknown history subcommand.", "red"))

def _show_history(limit=10):
    if not HISTORY_FILE.exists():
        print("[!] No history found.")
        return
    lines = HISTORY_FILE.read_text().splitlines()
    if limit is not None:
        lines = lines[-limit:]
    for line in lines:
        print(line)
    print()

def _find_history(key, value):
    if not HISTORY_FILE.exists():
        print("[!] No history found.")
        return
    lines = HISTORY_FILE.read_text().splitlines()
    found = False
    for line in lines:
        if f"{key}={value}" in line:
            print(line)
            found = True
    if not found:
        print(f"[!] No history entries found for {key}={value}.")
    print()

def _show_history_top_bottom(direction, n):
    if not HISTORY_FILE.exists():
        print("[!] No history found.")
        return
    lines = HISTORY_FILE.read_text().splitlines()
    if direction == "top":
        subset = lines[:n]
    elif direction == "bottom":
        subset = lines[-n:]
    else:
        print("[!] Direction must be 'top' or 'bottom'.")
        return
    for line in subset:
        print(line)
    print()

def handle_version():
    version = "v0.0.3"
    build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(color(f"\nPayloadBuilder X {version}", "green"))
    print(color(f"Build date: {build_date}\n", "cyan"))

# Helper to record history (called from build command)
def record_history(cfg, success):
    if not HISTORY_ENABLED:
        return
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("")
    lines = HISTORY_FILE.read_text().splitlines()
    serial = len(lines) + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"{k}={v}" for k, v in cfg.items()]
    status = "SUCCESS" if success else "FAIL"
    line = f"{serial}. {' '.join(parts)} timestamp={timestamp} {status}"
    with HISTORY_FILE.open("a") as f:
        f.write(line + "\n")

# def handle_build(cfg):

#     pt = cfg.get("payload_type")
#     if not pt:
#         print(color("[!] Please set payload_type first.", "red"))
#         return

#     profile = PAYLOAD_PROFILE.get(pt)
#     if not profile:
#         print(color(f"[!] Unknown payload_type '{pt}'.", "red"))
#         return

#     required = profile["required"]
#     defaults = profile["defaults"]

#     spec = {**defaults, **cfg}

#     missing = [opt for opt in required if not spec.get(opt)]
#     if missing:
#         print("\n" + color("[!] Missing required option(s):", "red"), ", ".join(missing))
#         print("    → Use: set OPTION VALUE   (TAB completes names/values)")
#         print("    → Or   list              (see * items that are still blank)\n")
#         return

#     errors = validate_config(spec)
#     if errors:
#         print("\n" + color("[!] Validation error(s):", "red"))
#         for e in errors:
#             print("    -", e)
#         print("    → Fix with  set OPTION VALUE\n")
#         return

#     print("\n" + color("[+] Building payload …", "green"))
#     try:
#         out_path = compile_payload(spec)
#     except Exception as exc:
#         print(color(f"[!] Build failed: {exc}\n", "red"))
#         return

#     # Polished Build Summary
#     print("\n+==================================================+")
#     print("| Build Summary                                    |")
#     print("+==================================================+")
#     print(f"| Payload Type   : {pt.ljust(40)}|")
#     print(f"| Build Time     : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
#     print("+--------------------------------------------------+")

#     # Determine all keys to print (required + optional that have value)
#     keys_to_show = profile["required"] + profile["optional"]
#     max_key_len = max(len(k) for k in keys_to_show)

#     for k in keys_to_show:
#         v = spec.get(k)
#         if v:
#             print(f"| {k.ljust(max_key_len)} : {str(v).ljust(40)}|")

#     print("+--------------------------------------------------+\n")

#     print(color(f"[✓] Payload saved to: {out_path}", "green"))

#     # For reverse_shell → print listener hint
#     if pt == "reverse_shell":
#         port = spec["port"]
#         print("\n" + color("[*] Listener hint:", "cyan"))
#         print(f"    nc -lvnp {port}")
#         print(f"    netcat -lvnp {port}")
#         print(f"    ncat -lv {port}")
#     print()

def _print_history_line(line, highlight=False, match=None):
    from .color_utils import color
    parts = line.split("timestamp=")
    config_part = parts[0].strip()
    rest = parts[1] if len(parts) > 1 else ""
    ts_part, result_part = rest.split(" result=") if " result=" in rest else (rest, "")
    ts_part = ts_part.strip()
    result_part = result_part.strip()

    # Build output line
    line_out = f"{color(ts_part, 'cyan')} "

    if "SUCCESS" in result_part:
        line_out += color("[✓] SUCCESS", "green")
    elif "FAIL" in result_part:
        line_out += color("[!] FAIL", "red")
    else:
        line_out += result_part

    # Print line with possible highlight
    if highlight and match:
        config_part = config_part.replace(match, color(match, "yellow"))
    print(f"{config_part} timestamp={line_out}")
