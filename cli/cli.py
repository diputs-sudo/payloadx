# pbx/cli/cli.py

from .core_shell import PBShell
from .ui_elements import show_banner, show_hacker_consent, show_welcome_message

def main():
    show_hacker_consent()
    show_banner()
    show_welcome_message()
    
    PBShell().cmdloop()

if __name__ == "__main__":
    main()
