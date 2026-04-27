import argparse
import sys
from utils.logger import Logger
from utils.helpers import validate_ip, validate_port, get_local_ip, is_port_free


def banner():
    print(r"""
   _____ _               _    _____ ___  
  / ____| |             | |  / ____|__ \ 
 | |  __| |__   ___  ___| |_| |       ) |
 | | |_ | '_ \ / _ \/ __| __| |      / / 
 | |__| | | | | (_) \__ \ |_| |____ / /_ 
  \_____|_| |_|\___/|___/\__|\_____/____|
                                          
  👻 GhostC2 — Command & Control Framework
     by Dreadonyx | github.com/Dreadonyx
     For authorized testing only.
    """)


def parse_args():
    parser = argparse.ArgumentParser(
        description="GhostC2 — Reverse shell C2 framework",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-l", "--listen", type=int, metavar="PORT",
                        help="Start listener on port and launch C2 console")
    parser.add_argument("-s", "--simple", type=int, metavar="PORT",
                        help="Simple netcat-style listener (no session management)")
    parser.add_argument("-g", "--generate", action="store_true",
                        help="Launch payload generator only")
    parser.add_argument("--lhost", metavar="IP",
                        help="Local host IP for payload generation")
    parser.add_argument("--lport", metavar="PORT",
                        help="Local port for payload generation")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Bind address for listener (default: 0.0.0.0)")
    return parser.parse_args()


def main():
    banner()
    args = parse_args()
    logger = Logger()

    # Payload generator only mode
    if args.generate:
        from payloads.generator import generate
        generate(lhost=args.lhost, lport=args.lport, logger=logger)
        return

    # Simple listener mode
    if args.simple:
        port = args.simple
        if not validate_port(port):
            logger.error(f"Invalid port: {port}")
            sys.exit(1)
        if not is_port_free(port):
            logger.error(f"Port {port} is already in use")
            sys.exit(1)

        from core.listener import Listener
        listener = Listener(host=args.host, port=port, logger=logger)
        logger.info("Simple mode — raw netcat-style listener")
        logger.info("Press Ctrl+C to stop\n")
        try:
            listener.start(background=False)
        except KeyboardInterrupt:
            listener.stop()
        return

    # Full C2 mode (default if -l given)
    port = args.listen or 4444
    if not validate_port(port):
        logger.error(f"Invalid port: {port}")
        sys.exit(1)
    if not is_port_free(port):
        logger.error(f"Port {port} is already in use")
        sys.exit(1)

    from core.session_manager import SessionManager
    from core.listener import Listener
    from core.console import Console

    sm = SessionManager()
    listeners = {}

    # Start initial listener
    listener = Listener(host=args.host, port=port, session_manager=sm, logger=logger)
    try:
        listener.start(background=True)
        listeners[port] = listener
    except Exception:
        sys.exit(1)

    logger.info(f"Local IP: {get_local_ip()}")
    logger.info("Type 'help' for commands\n")

    # Launch C2 console
    console = Console(sm, listeners, logger)
    console.run()


if __name__ == "__main__":
    main()
