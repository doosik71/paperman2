from datetime import datetime


status_message = ""
icons = {
    "debug": "🛠️",
    "info": "💡",
    "warning": "⚠️",
    "error": "🛑",
    "critical": "🚫",
}


def __now():
    return datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")


def log(icon: str, message: str) -> None:
    global status_message
    status_message = icon + " " + message

    print(__now(), icon, message, flush=True)


def debug(message) -> None:
    log(icons["debug"], message)


def info(message):
    log(icons["info"], message)


def warning(message):
    log(icons["warning"], message)


def error(message):
    log(icons["error"], message)


def critical(message):
    log(icons["critical"], message)
