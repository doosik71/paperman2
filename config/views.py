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
            SUMMARY_PROMPT = request.POST["SUMMARY_PROMPT"]
            PRESENTATION_PROMPT = request.POST["PRESENTATION_PROMPT"]

            set_config_value("GEMINI_API_KEY", GEMINI_API_KEY)
            set_config_value("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
            set_config_value("OLLAMA_REQUEST_URL", OLLAMA_REQUEST_URL)
            set_config_value("SUMMARY_PROMPT", SUMMARY_PROMPT)
            set_config_value("PRESENTATION_PROMPT", PRESENTATION_PROMPT)

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
    SUMMARY_PROMPT = get_config_value("SUMMARY_PROMPT")
    PRESENTATION_PROMPT = get_config_value("PRESENTATION_PROMPT")

    config = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
        "OLLAMA_REQUEST_URL": OLLAMA_REQUEST_URL,
        "SUMMARY_PROMPT": SUMMARY_PROMPT,
        "PRESENTATION_PROMPT": PRESENTATION_PROMPT,
    }

    return render(request, "config/config_detail.html", config)
