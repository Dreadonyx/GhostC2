from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)


class Logger:
    def info(self, msg):
        print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")

    def success(self, msg):
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")

    def error(self, msg):
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")

    def warning(self, msg):
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")

    def shell(self, session_id, msg):
        print(f"{Fore.MAGENTA}[Session {session_id}]{Style.RESET_ALL} {msg}")

    def incoming(self, ip, port):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Fore.GREEN}[{ts}] 🔗 New connection from {ip}:{port}{Style.RESET_ALL}")

    def prompt(self, session_id, cwd="~"):
        return input(f"{Fore.RED}ghost{Style.RESET_ALL}@{Fore.YELLOW}session-{session_id}{Style.RESET_ALL}:{Fore.CYAN}{cwd}{Style.RESET_ALL}$ ")

    def c2_prompt(self):
        return input(f"\n{Fore.RED}GhostC2{Style.RESET_ALL} {Fore.WHITE}>{Style.RESET_ALL} ")

    def section(self, msg):
        print(f"\n{Fore.CYAN}{'─'*50}\n  {msg}\n{'─'*50}{Style.RESET_ALL}")

    def banner_line(self, msg):
        print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
