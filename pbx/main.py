#!/usr/bin/env python3
# PayloadBuilder X – CLI v0.0.2
# 
# Key commands
# -------------
# list                      – show current config (* required)
# set OPT VAL[, OPT VAL…]   – update one or many options (TAB-complete)
# reset                     – clear all parameters
# clear                     – clear terminal
# build                     – compile payload (stub)
# help [cmd|opt]            – detailed help
# exit / quit               – leave shell

import cmd
import sys
import os 
import platform as _p
import shlex
import re
import difflib
from pathlib import Path
from typing import Dict, List, Optional

CONSENT_FILE = Path.home() / ".payloadbuilder_x_consent"   
CONSENT_ART = r"""
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
╚═════════════════════════════════════════════════════════════════╝
"""

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

def show_hacker_consent() -> None:
    if CONSENT_FILE.exists():
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
    except KeyboardInterrupt:
        print("\n✖ Interrupted. Exiting.")
        sys.exit(1)

    try:
        remember = input("→ Hide this banner in future runs? (yes/no): ").strip().lower()
        if remember in {"yes", "y"}:
            CONSENT_FILE.write_text("acknowledged\n")
            print("✓ Consent saved. You won't see this banner again.")
    except Exception as e:
        print(f"[!] Failed to save consent preference: {e}")
        sys.exit(1)

# === CLI Logic ===

sys.path.append(str(Path(__file__).resolve().parent))
from builder.compiler import compile_payload

OPTIONS = {
    "payload_type": ["reverse_shell", "keylogger", "dropper"],
    "language": ["python"],
    "platform": ["macos"],
    "LHOST": None,
    "LPORT": None,
    "callback_delay": None,
    "stealth": ["none", "xor", "obfuscate_vars"],
    "persistence": ["none", "mac_launch_agent"],
    "output_path": None,
    "filename": None,
    "variant": ["short", "medium", "long", "ultra"], 
    "build_mode": ["debug", "release", "dry-run"],
}

DESCR = {
    "payload_type": "Kind of payload to generate (reverse shell, dropper, …).",
    "language": "Source language for the generated payload.",
    "platform": "Target operating system (macOS in MVP).",
    "LHOST": "Listener IP for reverse connections.",
    "LPORT": "Listener port.",
    "callback_delay": "Delay (s) between callbacks/beacons.",
    "stealth": "Obfuscation layers to apply.",
    "persistence": "Persistence mechanism on target.",
    "output_path": "Folder for generated payload (default ./output/).",
    "filename": "Output filename (no extension).",
    "variant": "Length/Functions of the payload (short, medium, long, ultra) ",
    "build_mode": "debug / release / dry-run.",
}

DEFAULTS = {
    "output_path": "./output/",
    "callback_delay": "0",
    "stealth": "none",
    "persistence": "none",
    "variant": "short", 
    "build_mode": "debug",
}

PAYLOAD_REQS = {
    "reverse_shell": ["LHOST", "LPORT"],
    "keylogger": [],
    "dropper": ["persistence", "filename"],
}
BASE_REQ_NO = ["payload_type"]
BASE_REQ_WITH = ["payload_type", "language", "platform"]

CAP_MAP = {"lhost": "LHOST", "lport": "LPORT"}
def normalize_key(k): return CAP_MAP.get(k.lower(), k.lower())

def validate_config(cfg: Dict[str, str]) -> List[str]:
    errors = []
    if "LPORT" in cfg:
        try:
            port = int(cfg["LPORT"])
            if not (1 <= port <= 65535):
                errors.append("LPORT must be between 1 and 65535.")
        except ValueError:
            errors.append("LPORT must be a valid integer.")
    if "LHOST" in cfg:
        host = cfg["LHOST"]
        ipv4 = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        ipv6 = re.compile(r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$")
        if not (ipv4.match(host) or ipv6.match(host)):
            errors.append("LHOST must be a valid IPv4 or IPv6 address.")
    return errors

def typo_match(word: str, candidates: List[str]) -> Optional[str]:
    word = word.lower()
    matches = difflib.get_close_matches(word, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None

class PBShell(cmd.Cmd):
    intro = "\nPayloadBuilder X - type 'help' for commands.\n"
    prompt = "payloadx> "
    cfg: Dict[str, str] = {}

    def req(self):
        pt = self.cfg.get("payload_type")
        return (BASE_REQ_WITH if pt else BASE_REQ_NO) + PAYLOAD_REQS.get(pt, [])

    def do_set(self, arg: str):
        if not arg.strip():
            print("Usage: set OPTION VALUE[, OPTION VALUE...]")
            return
        for pair in [p.strip() for p in arg.split(",")]:
            parts = shlex.split(pair)
            if len(parts) < 2:
                print(f"[!] Skipped malformed pair: '{pair}'")
                continue
            opt, val = normalize_key(parts[0]), " ".join(parts[1:])
            if opt not in OPTIONS:
                print(f"[!] Unknown option: {opt}")
                continue
            allowed = OPTIONS[opt]
            if allowed and val not in allowed:
                print(f"[!] Invalid value for {opt}. Allowed: {', '.join(allowed)}")
                continue

            temp_cfg = self.cfg.copy()
            temp_cfg[opt] = val
            validation_errors = validate_config(temp_cfg)
            if validation_errors:
                print(f"[!] Invalid value for {opt}: {validation_errors[0]}")
                continue

            self.cfg[opt] = val
            print(f"{opt} = {val}")

    def complete_set(self, text: str, line: str, begidx: int, _end: int):
        arg_str = line[4:] if line.lower().startswith("set ") else line
        rel_idx = begidx - (4 if line.lower().startswith("set ") else 0)
        before_cursor = arg_str[:rel_idx]
        segment = before_cursor.split(",")[-1].lstrip()
        tokens = shlex.split(segment)
        if len(tokens) == 0 or (len(tokens) == 1 and not segment.endswith(" ")):
            return [o for o in OPTIONS if o.lower().startswith(text.lower())]
        opt = normalize_key(tokens[0])
        values = OPTIONS.get(opt) or []
        return [v for v in values if v.startswith(text)]

    def do_list(self, _):
        req_set = set(self.req())
        rows = [(f"{'*' if o in req_set else ' '} {o}", self.cfg.get(o, DEFAULTS.get(o, "")))
                for o in OPTIONS]
        col = max(len(l) for l, _ in rows) + 2
        print("\nCurrent configuration (* required)")
        print(f"{'Option'.ljust(col)}| Value")
        print(f"{'-'*col}+{'-'*30}")
        for left, right in rows:
            print(f"{left.ljust(col)}| {right}")
        print()

    def do_reset(self, _): self.cfg.clear(); print("✓ Reset.")
    def do_clear(self, _): 
        try: 
            if _p.system().lower().startswith("win"):
                os.system("cls")
            else:
                os.system("clear")
        except Exception:
            print("[!] Clear failed.")

    def do_build(self, _):
        spec = {**DEFAULTS, **self.cfg}
        missing = [opt for opt in self.req() if not spec.get(opt)]
        if missing:
            print("\n[!] Missing required option(s):", ", ".join(missing))
            print("    ➜ Use  set OPTION VALUE   (TAB completes names/values)")
            print("    ➜ Or   list              (see * items that are still blank)\n")
            return

        errors = validate_config(spec)
        if errors:
            print("\n[!] Validation error(s):")
            for e in errors:
                print("    -", e)
            print("    ➜ Fix with  set OPTION VALUE\n")
            return

        print("\n[+] Building payload …")
        try:
            out_path = compile_payload(spec)
        except Exception as exc:
            print(f"[!] Build failed: {exc}\n")
            return

        print("\n┌─ Build Summary ──────────────────────")
        width = max(len(k) for k in OPTIONS)
        for k in OPTIONS:
            v = spec.get(k)
            if v:
                print(f"│ {k.ljust(width)} : {v}")
        print("└────────────────────────────────────────\n")

        print(f"[✓] Payload saved to: {out_path}")

        if spec["payload_type"] == "reverse_shell":
            port = spec["LPORT"]
            print("\n[*] Listener hint:")
            print(f"    nc -lvnp {port}")
            print(f"    netcat -lvnp {port}")
            print(f"    ncat -lv {port}")
        print()

    def do_help(self, arg: str):
        topic = arg.strip().lower()
        builtin_cmds = {
            "list": "Show current configuration and which values are required.",
            "set": "Set one or more options. Format: set OPTION VALUE[, OPTION VALUE]",
            "reset": "Clear all current values and start fresh.",
            "clear": "Clear the terminal screen.",
            "build": "Build payload from the current configuration.",
            "help": "Show help for commands or options.",
            "exit": "Exit the shell.",
            "quit": "Alias for exit."
        }

        if not topic:
            print("\nCommands:")
            for cmd_name, desc in builtin_cmds.items():
                print(f"  {cmd_name:<10} - {desc}")
            print("\nOptions:")
            cur = set(self.req())
            for o in OPTIONS:
                star = "*" if o in cur else " "
                allowed = "free-text" if OPTIONS[o] is None else ", ".join(OPTIONS[o])
                print(f" {star} {o:<15} - {DESCR.get(o, '')} (values: {allowed})")
            print()
            return

        if topic in builtin_cmds:
            print(f"\nCommand: {topic}\n  {builtin_cmds[topic]}\n")
            return

        if topic in OPTIONS:
            allowed = "free-text" if OPTIONS[topic] is None else ", ".join(OPTIONS[topic])
            star = "*" if topic in self.req() else " "
            print(f"\n {star} {topic}\n   {DESCR.get(topic, '')}\n   Allowed: {allowed}\n")
        else:
            print(f"\n[!] Unknown command or option: {topic}")

    def complete_help(self, text, *_):
        command_keywords = ["list", "set", "reset", "clear", "build", "exit", "quit", "help"]
        return [x for x in list(OPTIONS) + command_keywords if x.startswith(text)]

    def do_exit(self, _): print("Bye!"); return True
    do_quit = do_exit
    def emptyline(self): pass

    def default(self, line: str):
        words = line.strip().split()
        if not words: return

        user_input = words[0].lower()
        args = " ".join(words[1:])

        all_cmds = [method[3:] for method in dir(self) if method.startswith("do_")]

        suggestion = typo_match(user_input, all_cmds)
        if suggestion:
            try:
                confirm = input(f"[~] Did you mean '{suggestion}'? (enter/n): ").strip().lower()
                if confirm in {"", "y", "yes"}:
                    return getattr(self, f"do_{suggestion}")(args)
            except KeyboardInterrupt:
                print("\n✖ Cancelled.")
                return
        print(f"[!] Unknown command: {user_input}")

def main():
    print(BANNER)
    show_hacker_consent()
    PBShell().cmdloop()

if __name__ == "__main__":
    main()
