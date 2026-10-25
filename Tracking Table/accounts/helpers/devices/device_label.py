import re


CLIENT_HINT_NAMES = "Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version"


def attach_device_client_hints(response):
    response["Accept-CH"] = CLIENT_HINT_NAMES
    response["Critical-CH"] = "Sec-CH-UA-Platform-Version"
    return response


def device_label_from_request(request):
    agent = request.META.get("HTTP_USER_AGENT", "") or ""
    parts = [
        part
        for part in (
            _device_family(agent),
            _platform(request, agent),
            _platform_version(request),
            _browser(agent),
        )
        if part
    ]
    return ", ".join(parts)[:100] or "НЕИЗВЕСТНО"


def _device_family(agent):
    if "iPhone" in agent:
        return "iPhone"
    if "iPad" in agent:
        return "iPad"
    if "iPod" in agent:
        return "iPod"
    android_model = re.search(r"Android [^;)]*;\s*([^;)]+)", agent)
    if android_model:
        model = re.sub(r"\s+Build/.*$", "", android_model.group(1)).strip()
        if model and model.lower() not in {"k", "mobile", "wv"} and len(model) > 1:
            return model
        return "Android"
    if "Macintosh" in agent or "Mac OS X" in agent:
        return "Mac"
    if "CrOS" in agent:
        return "Chromebook"
    if "Windows" in agent or "Linux" in agent:
        return "PC"
    return ""


def _platform(request, agent):
    hinted = _hint(request, "HTTP_SEC_CH_UA_PLATFORM")
    if hinted:
        return hinted
    if "iPhone" in agent or "iPod" in agent:
        return "iOS"
    if "iPad" in agent:
        return "iPadOS"
    if "Android" in agent:
        return "Android"
    if "Mac OS X" in agent or "Macintosh" in agent:
        return "macOS"
    if "Windows" in agent:
        return "Windows"
    if "CrOS" in agent:
        return "Chrome OS"
    if "Linux" in agent:
        return "Linux"
    return ""


def _platform_version(request):
    version = _hint(request, "HTTP_SEC_CH_UA_PLATFORM_VERSION")
    if version in {"", "0.0.0", "0"}:
        return ""
    return version


def _browser(agent):
    if "Edg/" in agent or "EdgiOS/" in agent:
        return "Edge"
    if "OPR/" in agent or "Opera" in agent:
        return "Opera"
    if "Chrome/" in agent or "CriOS/" in agent:
        return "Chrome"
    if "Firefox/" in agent or "FxiOS/" in agent:
        return "Firefox"
    if "Safari/" in agent:
        return "Safari"
    return ""


def _hint(request, meta_key):
    value = (request.META.get(meta_key, "") or "").strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1].strip()
    return value
