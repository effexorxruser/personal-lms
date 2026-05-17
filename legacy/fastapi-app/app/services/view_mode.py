from fastapi import Request


MOBILE_QUERY_VALUES = {"1", "true", "yes", "on", "mobile"}
MOBILE_USER_AGENT_TOKENS = ("iphone", "android", "mobile", "ipad")


def is_mobile_view(request: Request) -> bool:
    explicit_mobile = request.query_params.get("mobile", "").strip().lower()
    if explicit_mobile in MOBILE_QUERY_VALUES:
        return True

    explicit_view = request.query_params.get("view", "").strip().lower()
    if explicit_view == "mobile":
        return True

    user_agent = request.headers.get("user-agent", "").lower()
    return any(token in user_agent for token in MOBILE_USER_AGENT_TOKENS)
