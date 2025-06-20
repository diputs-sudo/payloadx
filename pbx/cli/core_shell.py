# pbx/cli/core_shell.py

import cmd
import shlex
import difflib
import os
import time
from pathlib import Path
import re

from . import command_handlers
from .config import PAYLOAD_PROFILE, BUILTIN_CMDS, OPTIONS_INFO, SUBCOMMANDS
from .color_utils import color
from .command_handlers import record_history
from pbx.builder import compiler, scanner 


class PBShell(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.cfg = {}
        self._last_complete_line = None

    intro = "\nPayloadBuilder X - type 'help' for commands.\n"
    prompt = color("payloadx ", "yellow") + color("> ", "cyan")
    cfg = {}

    def do_set(self, arg):
        if not arg.strip():
            print("Usage: set OPTION VALUE[, OPTION VALUE...] or set history SERIAL_NUM")
            return

        parts = shlex.split(arg)

        # Handle set history SERIAL_NUM
        if parts[0].lower() == "history" and len(parts) == 2:
            serial_num = parts[1]
            serial_num = re.sub(r"\x1b\[[0-9;]*m", "", serial_num)
            path = Path(__file__).resolve().parent.parent / "history" / "history.log"

            if not path.exists():
                print("[!] No history found.")
                return

            lines = path.read_text().splitlines()

            for line in lines:
                if line.startswith(f"{serial_num}. "):
                    try:
                        kv_part = line.split(". ", 1)[1]
                        kv_tokens = kv_part.split(" timestamp=")[0].split()

                        self.cfg.clear()
                        for token in kv_tokens:
                            if "=" in token:
                                k, v = token.split("=", 1)
                                self.cfg[k] = v

                        print(f"✓ Restored config from history #{serial_num}.")
                        command_handlers.handle_list(self.cfg)
                        return

                    except Exception as e:
                        print(f"[!] Failed to parse history line: {e}")
                        return

            print(f"[!] No history entry #{serial_num} found.")
            return

        # Normal set OPTION VALUE[, OPTION VALUE...]
        for pair in [p.strip() for p in arg.split(",")]:
            tokens = shlex.split(pair)
            if len(tokens) < 2:
                print(f"[!] Skipped malformed pair: '{pair}'")
                continue

            opt, val = tokens[0], " ".join(tokens[1:])

            # Special case: first time, allow setting payload_type
            if "payload_type" not in self.cfg:
                if opt == "history":
                    print("[!] Use: set history SERIAL_NUM (not as a config option)")
                    return

                if opt != "payload_type":
                    available = ", ".join(PAYLOAD_PROFILE.keys())
                    print("[!] Please set payload_type first. Use: set payload_type VALUE")
                    print(f"    Available payload_types: {available}")
                    return

                if val not in PAYLOAD_PROFILE:
                    print(f"[!] Invalid payload_type '{val}'. Available: {', '.join(PAYLOAD_PROFILE.keys())}")
                    return

                self.cfg["payload_type"] = val
                print(f"✓ payload_type = {val}")
                print("     → Use: list to see required/optional options.")
                return

            # After payload_type is set → normal processing
            pt = self.cfg.get("payload_type")
            profile = PAYLOAD_PROFILE.get(pt)

            if not profile:
                print(f"[!] Unknown payload_type '{pt}'.")
                return

            valid_keys = profile["required"] + profile["optional"]

            if opt not in valid_keys and opt != "payload_type":
                print(f"[!] Unknown option: {opt}")
                continue

            temp_cfg = self.cfg.copy()
            temp_cfg[opt] = val

            validation_errors = command_handlers.validate_config(temp_cfg)

            if validation_errors:
                print(f"[!] Invalid value for {opt}: {validation_errors[0]}")
                continue

            self.cfg[opt] = val
            print(f"{opt} = {val}")

    def _print_block(self, lines):
        """
        Print multiple lines cleanly and reprint prompt.
        """
        for line in lines:
            print("  " + line)
        print()  # spacing
        self.stdout.write(self.prompt)
        self.stdout.flush()

    def complete_set(self, text, line, begidx, _end):

        if line.strip().startswith("set history"):
            history_path = Path(__file__).resolve().parent.parent / "history" / "history.log"
            if not history_path.exists():
                return []

            lines = history_path.read_text().splitlines()
            if not lines:
                return []

            # Only print once per input session
            if not self._printed_history_hint:
                self._print_block(lines[-3:])
                self._printed_history_hint = True

            return []  # ← the key fix: return NOTHING so readline doesn't try to complete it

        # Reset hint if no longer in `set history`
        self._printed_history_hint = False

        # Special case: first time → allow payload_type and history
        if "payload_type" not in self.cfg:
            arg_str = line[4:] if line.lower().startswith("set ") else line
            rel_idx = begidx - (4 if line.lower().startswith("set ") else 0)
            before_cursor = arg_str[:rel_idx]
            segment = before_cursor.split(",")[-1].lstrip()
            tokens = shlex.split(segment)

            if len(tokens) == 0 or (len(tokens) == 1 and not segment.endswith(" ")):
                return [k for k in ["payload_type", "history"] if k.startswith(text)]

            if tokens[0] == "payload_type":
                return [pt for pt in PAYLOAD_PROFILE.keys() if pt.startswith(text)]

            return []

        # Normal completion after payload_type is set
        pt = self.cfg.get("payload_type")
        profile = PAYLOAD_PROFILE.get(pt)

        if not profile:
            return []

        arg_str = line[4:] if line.lower().startswith("set ") else line
        rel_idx = begidx - (4 if line.lower().startswith("set ") else 0)
        before_cursor = arg_str[:rel_idx]
        segment = before_cursor.split(",")[-1].lstrip()
        tokens = shlex.split(segment)

        valid_keys = profile["required"] + profile["optional"]

        if len(tokens) == 0 or (len(tokens) == 1 and not segment.endswith(" ")):
            return [o for o in valid_keys if o.startswith(text)]

        opt = tokens[0]
        if opt not in valid_keys:
            return []

        allowed_values = OPTIONS_INFO.get(opt, {}).get("allowed_values")

        if allowed_values and isinstance(allowed_values, dict):
            return [v for v in allowed_values.keys() if v.startswith(text)]

        return []

    def do_list(self, _):
        command_handlers.handle_list(self.cfg)

    def do_reset(self, _):
        self.cfg.clear()
        print(color("✓ Reset.", "green"))

    def do_clear(self, _):
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception:
            print("[!] Clear failed.")

    def do_build(self, _):
        from pbx.builder import compiler
        from pbx.cli.command_handlers import record_history
        from pbx.cli.config import PAYLOAD_PROFILE

        pt = self.cfg.get("payload_type")
        if not pt:
            print(color("[!] Please set payload_type first.", "red"))
            return

        profile = PAYLOAD_PROFILE.get(pt)
        if not profile:
            print(color(f"[!] Unknown payload_type '{pt}'.", "red"))
            return

        required = profile["required"]
        defaults = profile["defaults"]

        spec = defaults.copy()
        spec.update(self.cfg)

        missing = [key for key in required if not spec.get(key)]
        if missing:
            print(color("\n[!] Missing required option(s):", "red") + " " + ", ".join(missing))
            print("    ➔ Use  set OPTION VALUE   (TAB completes names/values)")
            print("    ➔ Or   list              (see * items that are still blank)\n")
            return

        errors = compiler.validate_config(spec)
        if errors:
            print(color("\n[!] Validation error(s):", "red"))
            for e in errors:
                print(f"    - {e}")
            print("    ➔ Fix with  set OPTION VALUE\n")
            return

        print(color("\n[+] Building payload …", "green"))

        try:
            out_path = compiler.build(spec)
        except Exception as exc:
            print(color(f"[!] Build failed: {exc}", "red"))
            record_history(self.cfg, success=False)
            return

        print("\n+==================================================+")
        print("| Build Summary                                    |")
        print("+==================================================+")
        print(f"| Payload Type   : {pt.ljust(40)}|")
        print(f"| Build Time     : {time.strftime('%Y-%m-%d %H:%M:%S')}              |")
        print("+--------------------------------------------------+")

        keys_to_show = profile["required"] + profile["optional"]
        max_key_len = max(len(k) for k in keys_to_show)

        for k in keys_to_show:
            v = spec.get(k)
            if v:
                print(f"| {k.ljust(max_key_len)} : {str(v).ljust(40)}|")

        print("+--------------------------------------------------+")
        print(color(f"[✓] Payload saved to: {out_path}", "green"))

        if pt == "reverse_shell":
            port = spec["port"]
            print("\n" + color("[*] Listener hint:", "cyan"))
            print(f"    nc -lvnp {port}")
            print(f"    netcat -lvnp {port}")
            print(f"    ncat -lv {port}")
        print()

        record_history(self.cfg, success=True)

    def do_scan(self, arg):
        from pbx.builder import scanner
        target = arg.strip().lower()

        if not target:
            print("[!] Usage: scan all|blocks|plugins")
            return

        print(color(f"[*] Scanning for {target} ...", "cyan"))

        try:
            if target == "all":
                count = scanner.scan_all()
            elif target == "blocks":
                count = scanner.scan_blocks("blocks")
            elif target == "plugins":
                count = scanner.scan_plugins()
            else:
                print(f"[!] Unknown scan target: {target}")
                return
            print(color(f"[✓] Scan complete: {count} item(s) indexed.", "green"))
        except Exception as e:
            print(color(f"[!] Scan failed: {e}", "red"))

    def do_config(self, arg):
        command_handlers.handle_config(self.cfg, arg)

    def do_wizard(self, _):
        command_handlers.handle_wizard(self.cfg)

    def do_history(self, arg):
        command_handlers.handle_history(self.cfg, arg)

    def do_version(self, _):
        command_handlers.handle_version()

    def do_help(self, arg):
        topic = arg.strip().lower()

        option_keys = []
        pt = self.cfg.get("payload_type")

        if pt and pt in PAYLOAD_PROFILE:
            profile = PAYLOAD_PROFILE[pt]
            option_keys = profile["required"] + profile["optional"]

        if not option_keys:
            option_keys = list(OPTIONS_INFO.keys())

        if not topic:
            print("\nCommands:")
            for cmd_name, desc in BUILTIN_CMDS.items():
                print(f"  {color(cmd_name, 'green'):<10} - {desc}")

            print("\nOptions:")
            for o in option_keys:
                star = "*" if pt and o in PAYLOAD_PROFILE[pt]["required"] else " "
                desc = OPTIONS_INFO.get(o, {}).get("description", "(no description)")
                print(f" {star} {color(o, 'cyan')} - {desc}")

            print()
            return

        if topic in BUILTIN_CMDS:
            print(f"\nCommand: {color(topic, 'green')}\n  {BUILTIN_CMDS[topic]}\n")
            return

        if topic in OPTIONS_INFO:
            info = OPTIONS_INFO[topic]
            print(f"\n{color(topic, 'cyan')}")
            print(f"  {info['description']}\n")

            allowed_values = info.get("allowed_values")

            if allowed_values is None:
                print("  Allowed: free-text\n")
            else:
                print("  Allowed values:")
                for k, v in allowed_values.items():
                    print(f"    {k:<10} - {v}")
                print()
            return

        print(f"\n{color('[!] Unknown command or option: ' + topic, 'red')}")

    def complete_help(self, text, line, begidx, endidx):
        command_keywords = list(BUILTIN_CMDS.keys())
        payload_types = list(PAYLOAD_PROFILE.keys())
        option_keywords = list(OPTIONS_INFO.keys())

        all_keywords = command_keywords + payload_types + option_keywords

        if not text:
            return sorted(all_keywords)

        return [x for x in all_keywords if x.startswith(text)]

    def complete_history(self, text, line, begidx, endidx):
        return self.dynamic_complete_subcommand("history", text, line, begidx, endidx)

    def complete_config(self, text, line, begidx, endidx):
        return self.dynamic_complete_subcommand("config", text, line, begidx, endidx)

    def complete_scan(self, text, line, begidx, endidx):
        return self.dynamic_complete_subcommand("scan", text, line, begidx, endidx)

    def dynamic_complete_subcommand(self, cmd_name, text, line, begidx, endidx):
        subcmds = SUBCOMMANDS.get(cmd_name, [])
        split_line = line.strip().split()

        if len(split_line) == 1:
            return [s for s in subcmds if s.startswith(text)]

        if len(split_line) == 2 and not line.endswith(" "):
            return [s for s in subcmds if s.startswith(split_line[1])]

        if cmd_name == "history" and split_line[1] == "show":
            if len(split_line) == 2 and line.endswith(" "):
                return [s for s in ["top", "bottom"] if s.startswith(text)]
            if len(split_line) == 3 and not line.endswith(" "):
                return [s for s in ["top", "bottom"] if s.startswith(split_line[2])]

        return []

    def do_exit(self, _):
        if self.cfg.get("payload_type"):
            from pbx.cli.command_handlers import record_history
            record_history(self.cfg, success=False, on_exit=True)
            print(color("[*] Saved current config to history on exit.", "cyan"))
        print("Bye!")
        return True

    def do_quit(self, _):
        return self.do_exit(_)

    def emptyline(self):
        pass

    def default(self, line):
        words = line.strip().split()

        if not words:
            return

        user_input = words[0].lower()
        args = " ".join(words[1:])

        all_cmds = [method[3:] for method in dir(self) if method.startswith("do_")]
        suggestion = command_handlers.typo_match(user_input, all_cmds)

        if suggestion:
            try:
                confirm = input(f"[~] Did you mean '{suggestion}'? (enter/n): ").strip().lower()
                if confirm in {"", "y", "yes"}:
                    return getattr(self, f"do_{suggestion}")(args)
            except KeyboardInterrupt:
                print("\n✖ Cancelled.")
                return

        print(color(f"[!] Unknown command: {user_input}", "red"))