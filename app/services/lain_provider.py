from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class LainProviderRequest:
    api_key: str
    model: str
    timeout_seconds: int
    system_prompt: str
    user_prompt: str


class LainProviderError(RuntimeError):
    pass


def _extract_openai_text(payload: dict) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    fragments: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            candidate = content.get("text") or content.get("output_text")
            if isinstance(candidate, str) and candidate.strip():
                fragments.append(candidate.strip())
    return "\n".join(fragments).strip()


def request_lain_reply(request: LainProviderRequest) -> str:
    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {request.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": request.model,
                "instructions": request.system_prompt,
                "input": request.user_prompt,
                "temperature": 0.2,
                "max_output_tokens": 420,
            },
            timeout=request.timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LainProviderError("Lain provider request failed") from exc

    text = _extract_openai_text(response.json())
    if not text:
        raise LainProviderError("Empty AI helper response")
    return text
