from __future__ import annotations
import time
import re
from solution.instrument import observed_call
from telemetry.logger import logger
from telemetry.redact import redact

def mitigate(call_next, question, config, context):
    # 1. INPUT SANITIZATION (Prompt Injection Defense)
    # Strip customer notes ("GHI CHÚ", "GHI CHU", "NOTE") that might contain injections
    clean_question = question
    clean_question = re.sub(r'(?i)(ghi\s*chú|ghi\s*chu|note)[:\-\s].*', '', clean_question).strip()

    # 2. CACHING (Thread-safe caching)
    cache = context.get("cache")
    cache_lock = context.get("cache_lock")
    cache_key = clean_question.lower().strip()

    if cache is not None and cache_lock is not None:
        with cache_lock:
            if cache_key in cache:
                if logger:
                    logger.log_event("CACHE_HIT", {
                        "qid": context.get("qid"),
                        "question": question,
                        "clean_question": clean_question
                    })
                return cache[cache_key]

    # 3. RETRY ON ERROR
    max_retries = 3
    last_exc = None
    res = None

    for attempt in range(max_retries):
        try:
            res = observed_call(call_next, clean_question, config, context)
            
            # If the status is a wrapper error or a known transient error, we retry
            if res.get("status") == "wrapper_error":
                time.sleep(0.5 * (2 ** attempt))
                continue
            break
        except Exception as e:
            last_exc = e
            with open("wrapper_errors.txt", "a", encoding="utf-8") as f:
                f.write(f"Attempt {attempt} exception: {str(e)}\n")
                import traceback
                traceback.print_exc(file=f)
            time.sleep(0.5 * (2 ** attempt))

    if res is None:
        if last_exc:
            with open("wrapper_errors.txt", "a", encoding="utf-8") as f:
                f.write(f"Final failure raising: {str(last_exc)}\n")
            raise last_exc
        return {"answer": "Error occurred during agent execution.", "status": "wrapper_error"}

    # 4. OUTPUT PII REDACTION
    if res.get("answer"):
        redacted_answer, _ = redact(res["answer"])
        res["answer"] = redacted_answer

    # Save to cache if successful
    if cache is not None and cache_lock is not None and res.get("status") == "ok":
        with cache_lock:
            cache[cache_key] = res

    return res