## CLI Architecture Overview

The CLI is implemented as a lightweight interactive shell based on `cmd.Cmd`.  
It is intentionally designed to be fast, clean, and simple to extend.

Flow:

1. `cli.py` → Entry point. Handles initial UX flow:
    - show_hacker_consent()
    - show_banner()
    - show_welcome_message()
    - Launches PBShell().cmdloop()

2. `core_shell.py` → Defines PBShell class:
    - Owns prompt and shell loop.
    - Delegates all `do_*` commands to `command_handlers.py`.

3. `command_handlers.py` → Implements actual command logic.
    - Each `handle_*` function implements a command (set, list, reset, build, etc).

4. `config.py` → Central config:
    - Defines OPTIONS, DEFAULTS, BUILTIN_CMDS, etc.

5. `ui_elements.py` → Handles visual elements and UX flow:
    - Banner
    - Consent screen and signature
    - Welcome message

---

## Running the CLI

For development:

```bash
python -m pbx.cli.cli
```
After `pip install .`:    
```bash
payloadx
```

---

## Philosophy
The CLI is intentionally lightweight:

- No external CLI frameworks
- Based on Python standard library cmd.Cmd
- Minimal CPU/memory footprint
- Fast startup and operator-friendly experience
- Designed to be hackable and easy to extend

---

## Planned Commands

- `scan` → Scan for available blocks / addons / plugins.
- `config save/load` → Save/load CLI configs for reproducible builds.
- `wizard` → Optional guided build wizard for fast build flows.
- `history` → View and replay previous builds (backtrack build history).
- `version` → Show current PayloadBuilder X version.