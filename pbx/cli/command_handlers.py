# pbx/cli/command_handlers.py

import os
import sys
import shlex
import platform as _p
import re
import difflib
from .config import OPTIONS, DESCR, DEFAULTS, PAYLOAD_REQS, BASE_REQ_NO, BASE_REQ_WITH, CAP_MAP, BUILTIN_CMDS
# from pbx.builder.compiler import compile_payload   # Uncomment when ready

def normalize_key(k): return CAP_MAP.get(k.lower(), k.lower())

def validate_config(cfg):
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

def handle_set(cfg, arg):
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

        temp_cfg = cfg.copy()
        temp_cfg[opt] = val
        validation_errors = validate_config(temp_cfg)
        if validation_errors:
            print(f"[!] Invalid value for {opt}: {validation_errors[0]}")
            continue

        cfg[opt] = val
        print(f"{opt} = {val}")

def handle_list(cfg):
    pt = cfg.get("payload_type")
    req_set = set((BASE_REQ_WITH if pt else BASE_REQ_NO) + PAYLOAD_REQS.get(pt, []))
    rows = [(f"{'*' if o in req_set else ' '} {o}", cfg.get(o, DEFAULTS.get(o, "")))
            for o in OPTIONS]
    col = max(len(l) for l, _ in rows) + 2
    print("\nCurrent configuration (* required)")
    print(f"{'Option'.ljust(col)}| Value")
    print(f"{'-'*col}+{'-'*30}")
    for left, right in rows:
        print(f"{left.ljust(col)}| {right}")
    print()

def handle_reset(cfg):
    cfg.clear()
    print("✓ Reset.")

def handle_clear():
    try:
        if _p.system().lower().startswith("win"):
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        print("[!] Clear failed.")

def handle_build(cfg):
    spec = {**DEFAULTS, **cfg}
    pt = spec.get("payload_type")
    req_set = (BASE_REQ_WITH if pt else BASE_REQ_NO) + PAYLOAD_REQS.get(pt, [])
    missing = [opt for opt in req_set if not spec.get(opt)]
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
        # out_path = compile_payload(spec)   # Uncomment when ready
        out_path = "./output/example_payload.py"  # Placeholder for now
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

def handle_help(cfg, arg):
    topic = arg.strip().lower()

    pt = cfg.get("payload_type")
    req_set = set((BASE_REQ_WITH if pt else BASE_REQ_NO) + PAYLOAD_REQS.get(pt, []))

    if not topic:
        print("\nCommands:")
        for cmd_name, desc in BUILTIN_CMDS.items():
            print(f"  {cmd_name:<10} - {desc}")
        print("\nOptions:")
        for o in OPTIONS:
            star = "*" if o in req_set else " "
            allowed = "free-text" if OPTIONS[o] is None else ", ".join(OPTIONS[o])
            print(f" {star} {o:<15} - {DESCR.get(o, '')} (values: {allowed})")
        print()
        return

    if topic in BUILTIN_CMDS:
        print(f"\nCommand: {topic}\n  {BUILTIN_CMDS[topic]}\n")
        return

    if topic in OPTIONS:
        allowed = "free-text" if OPTIONS[topic] is None else ", ".join(OPTIONS[topic])
        star = "*" if topic in req_set else " "
        print(f"\n {star} {topic}\n   {DESCR.get(topic, '')}\n   Allowed: {allowed}\n")
    else:
        print(f"\n[!] Unknown command or option: {topic}")

# Optional: typo_match if you want to keep it
def typo_match(word, candidates):
    word = word.lower()
    matches = difflib.get_close_matches(word, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None
