from balsa import get_logger

from backupjca import __application_name__

last_line = ""

log = get_logger(__application_name__)


def print_log(s):
    global last_line
    log.info(s)
    print(f"\r{' '*len(last_line)}", end="", flush=True)  # erase last line
    print(f"\r{s}", end="", flush=True)
    last_line = s
