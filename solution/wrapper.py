import json
import sys
import uuid

import httpx


def load_config():
    with open("solution/config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def call_agent(question: str, user_id: str = "public_user", session_id: str = "public_session", feature: str = "qa"):
    config = load_config()
    base_url = config.get("base_url", "http://127.0.0.1:8000")
    chat_endpoint = config.get("chat_endpoint", "/chat")
    timeout_seconds = config.get("timeout_seconds", 30)

    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "feature": feature,
        "message": question
    }

    headers = {
        "x-request-id": f"req-{uuid.uuid4().hex[:8]}"
    }

    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.post(
            f"{base_url}{chat_endpoint}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


def main():
    raw = sys.stdin.read().strip()

    if raw:
        try:
            item = json.loads(raw)
            question = item.get("question") or item.get("message") or raw
        except json.JSONDecodeError:
            question = raw
    else:
        question = "Explain monitoring, tracing, and logging."

    result = call_agent(question)

    output = {
        "answer": result.get("answer"),
        "correlation_id": result.get("correlation_id"),
        "latency_ms": result.get("latency_ms"),
        "tokens_in": result.get("tokens_in"),
        "tokens_out": result.get("tokens_out"),
        "cost_usd": result.get("cost_usd"),
        "quality_score": result.get("quality_score")
    }

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()