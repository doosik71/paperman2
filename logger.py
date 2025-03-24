from datetime import datetime


def __now():
    return datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")


def debug(message):
    print(__now(), "[DEBUG]", message)


def info(message):
    print(__now(), "[INFO]", message)


def warning(message):
    print(__now(), "[WARNING]", message)


def error(message):
    print(__now(), "[ERROR]", message)


def critical(message):
    print(__now(), "[CRITICAL]", message)
