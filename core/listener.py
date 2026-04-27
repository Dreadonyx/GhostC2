import socket
import threading
from utils.logger import Logger


class Listener:
    def __init__(self, host="0.0.0.0", port=4444, session_manager=None, logger=None):
        self.host = host
        self.port = port
        self.session_manager = session_manager
        self.logger = logger or Logger()
        self.server = None
        self.running = False
        self._thread = None

    def start(self, background=True):
        """Start the TCP listener."""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(10)
            self.running = True
            self.logger.success(f"Listening on {self.host}:{self.port}")

            if background:
                self._thread = threading.Thread(target=self._accept_loop, daemon=True)
                self._thread.start()
            else:
                self._accept_loop()

        except OSError as e:
            self.logger.error(f"Could not bind to {self.host}:{self.port} — {e}")
            raise

    def _accept_loop(self):
        """Accept incoming connections in a loop."""
        self.server.settimeout(1.0)
        while self.running:
            try:
                conn, addr = self.server.accept()
                self._handle_new_connection(conn, addr)
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_new_connection(self, conn, addr):
        """Register and initialize new session."""
        self.logger.incoming(addr[0], addr[1])

        if self.session_manager:
            session = self.session_manager.add(conn, addr)
            self.logger.success(f"Session {session.id} opened — fetching sysinfo...")

            # Fetch sysinfo in background thread
            t = threading.Thread(target=self._init_session, args=(session,), daemon=True)
            t.start()
        else:
            # Simple mode — raw interaction
            self._simple_interact(conn, addr)

    def _init_session(self, session):
        """Initialize session with sysinfo."""
        import time
        time.sleep(0.5)  # Give shell time to stabilize
        session.get_sysinfo()
        self.logger.success(
            f"Session {session.id} ready | "
            f"User: {session.user} | "
            f"OS: {session.os} | "
            f"Host: {session.hostname}"
        )

    def _simple_interact(self, conn, addr):
        """Raw netcat-style interaction."""
        import sys
        self.logger.info(f"Simple mode — raw shell from {addr[0]}:{addr[1]}")
        self.logger.info("Type 'exit' to close\n")

        conn.settimeout(None)
        try:
            while True:
                cmd = input("$ ")
                if cmd.lower() in ("exit", "quit"):
                    break
                conn.send((cmd + "\n").encode())
                output = b""
                conn.settimeout(3)
                try:
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        output += chunk
                        if len(chunk) < 4096:
                            break
                except socket.timeout:
                    pass
                print(output.decode("utf-8", errors="ignore"), end="")
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            conn.close()
            self.logger.warning("Simple session closed")

    def stop(self):
        """Stop the listener."""
        self.running = False
        if self.server:
            try:
                self.server.close()
            except Exception:
                pass
        self.logger.warning(f"Listener on port {self.port} stopped")
