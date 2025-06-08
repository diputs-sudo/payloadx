# pbx/cli/core_shell.py

import cmd
import shlex
import difflib
from . import command_handlers
from .config import OPTIONS, CAP_MAP, BUILTIN_CMDS

class PBShell(cmd.Cmd):
    intro = "\nPayloadBuilder X - type 'help' for commands.\n"
    prompt = "payloadx> "
    cfg = {}

    def req(self):
        pt = self.cfg.get("payload_type")
        from .config import BASE_REQ_NO, BASE_REQ_WITH, PAYLOAD_REQS
        return (BASE_REQ_WITH if pt else BASE_REQ_NO) + PAYLOAD_REQS.get(pt, [])

    def do_set(self, arg):
        command_handlers.handle_set(self.cfg, arg)

    def complete_set(self, text, line, begidx, _end):
        from .config import OPTIONS, CAP_MAP
        def normalize_key(k): return CAP_MAP.get(k.lower(), k.lower())

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
        command_handlers.handle_list(self.cfg)

    def do_reset(self, _):
        command_handlers.handle_reset(self.cfg)

    def do_clear(self, _):
        command_handlers.handle_clear()

    def do_build(self, _):
        command_handlers.handle_build(self.cfg)

    def do_help(self, arg):
        command_handlers.handle_help(self.cfg, arg)

    def complete_help(self, text, *_):
        return [x for x in list(OPTIONS) + list(BUILTIN_CMDS) if x.startswith(text)]

    def do_exit(self, _):
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
        print(f"[!] Unknown command: {user_input}")
