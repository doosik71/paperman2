import logger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *


@login_required
def config_detail(request):
    """
    Get config page.
    """

    if request.method == "POST":
        try:
            GEMINI_API_KEY = request.POST["GEMINI_API_KEY"]
            OPENROUTER_API_KEY = request.POST["OPENROUTER_API_KEY"]
            OLLAMA_REQUEST_URL = request.POST["OLLAMA_REQUEST_URL"]
            prompt = request.POST["prompt"]

            set_config_value("GEMINI_API_KEY", GEMINI_API_KEY)
            set_config_value("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
            set_config_value("OLLAMA_REQUEST_URL", OLLAMA_REQUEST_URL)
            set_config_value("prompt", prompt)

            message = "Config updated"
            messages.success(request, message)
            logger.info(message)

        except Exception as e:
            message = f"Error: {e}"
            messages.error(request, message)
            logger.error(message)

    GEMINI_API_KEY = get_config_value("GEMINI_API_KEY")
    OPENROUTER_API_KEY = get_config_value("OPENROUTER_API_KEY")
    OLLAMA_REQUEST_URL = get_config_value("OLLAMA_REQUEST_URL")
    prompt = get_config_value("prompt")

    config = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
        "OLLAMA_REQUEST_URL": OLLAMA_REQUEST_URL,
        "prompt": prompt,
    }

    return render(request, "config/config_detail.html", config)
