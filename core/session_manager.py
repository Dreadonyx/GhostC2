import threading
from colorama import Fore, Style


class SessionManager:
    def __init__(self):
        self._sessions = {}
        self._lock = threading.Lock()
        self._next_id = 1

    def add(self, conn, addr):
        """Register a new session. Returns session object."""
        from core.session import Session
        with self._lock:
            sid = self._next_id
            self._next_id += 1
            session = Session(sid, conn, addr)
            self._sessions[sid] = session
        return session

    def get(self, session_id):
        """Get session by ID."""
        return self._sessions.get(int(session_id))

    def remove(self, session_id):
        """Remove and close a session."""
        sid = int(session_id)
        with self._lock:
            session = self._sessions.pop(sid, None)
            if session:
                session.close()
        return session is not None

    def all(self):
        """Return all sessions."""
        return dict(self._sessions)

    def alive(self):
        """Return only alive sessions."""
        return {sid: s for sid, s in self._sessions.items() if s.alive}

    def cleanup(self):
        """Remove dead sessions."""
        with self._lock:
            dead = [sid for sid, s in self._sessions.items() if not s.alive]
            for sid in dead:
                self._sessions.pop(sid)
        return len(dead)

    def count(self):
        return len(self._sessions)

    def print_table(self):
        """Print sessions table."""
        sessions = self.all()
        if not sessions:
            print(f"  {Fore.YELLOW}No active sessions{Style.RESET_ALL}")
            return

        header = f"{'ID':<5} {'IP':<18} {'PORT':<8} {'OS':<10} {'USER':<15} {'HOST':<20} {'TIME':<12} {'ALIVE'}"
        print(f"\n  {Fore.CYAN}{header}{Style.RESET_ALL}")
        print(f"  {'─'*90}")

        for sid, s in sessions.items():
            alive_str = f"{Fore.GREEN}✓{Style.RESET_ALL}" if s.alive else f"{Fore.RED}✗{Style.RESET_ALL}"
            print(f"  {str(sid):<5} {s.ip:<18} {str(s.port):<8} {s.os:<10} {s.user:<15} {s.hostname:<20} {s.duration:<12} {alive_str}")
        print()
