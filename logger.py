from datetime import datetime


status_message = ""


def __now():
    return datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")


def debug(message):
    global status_message
    status_message = "🛠️ " + str(message)
    
    print(__now(), status_message)


def info(message):
    global status_message
    status_message = "💡 " + str(message)

    print(__now(), status_message)


def warning(message):
    global status_message
    status_message = "⚠️ " + str(message)

    print(__now(), status_message)


def error(message):
    global status_message
    status_message = "🚫 " + str(message)

    print(__now(), status_message)


def critical(message):
    global status_message
    status_message = "🛑 " + str(message)

    print(__now(), status_message)
