# Wrapper API

Tệp `solution/wrapper.py` phải định nghĩa hàm:

```python
def mitigate(call_next, question, config, context):
    # call_next(question, config) -> result   (cách DUY NHẤT để giao tiếp với agent)
    # context = {"session_id", "turn_index", "qid",
    #            "cache": <shared dict across requests>, "cache_lock": <threading.Lock>}
    # Trả về một dict kết quả có cùng cấu trúc với đầu ra của run_agent
    return call_next(question, config)
```

Cấu trúc của `result`:
```python
{"answer": str|None, "status": "ok|loop|max_steps|no_action|wrapper_error",
 "steps": int, "trace": [...],
 "meta": {"latency_ms": int, "usage": {"prompt_tokens","completion_tokens","total_tokens"},
          "model": str, "provider": str, "session_id": str, "turn_index": int,
          "tools_used": [...]}}
```

## Các thao tác hợp lệ
- Tự động thử lại (retry) / backoff, lưu bộ nhớ đệm cache (quá trình chạy là bất đồng bộ và đồng thời — hãy bảo vệ trạng thái chia sẻ bằng `context["cache_lock"]`), điều hướng request đến model rẻ/local hơn, làm sạch đầu vào (ví dụ: bóc tách ghi chú đơn hàng bị injection), làm sạch đầu ra (redaction), xác thực tính toán số học/guardrail, cơ chế fallback, reset session.
- **Điều hướng Prompt (Prompt routing)** — ghi đè hệ thống prompt của agent trên mỗi yêu cầu cụ thể:
  ```python
  conf = dict(config); conf["system_prompt"] = my_better_prompt
  result = call_next(question, conf)
  ```
- Hệ thống log/trace/metrics của riêng bạn (đây CHÍNH LÀ khả năng quan sát - observability của bạn). Chỉ import thư viện chuẩn của Python và gói `telemetry/` được cung cấp kèm theo.

## Các thao tác không hợp lệ (Bị selfcheck từ chối / nhận điểm 0)
Hardcode câu trả lời; sử dụng bảng tra cứu câu hỏi→câu trả lời; import các module nội bộ của simulator như `observathon_sim._*` hoặc `observathon_score`; đọc các tệp hướng dẫn của giảng viên; sử dụng các thư viện mạng bên ngoài như `socket`/`urllib`/`requests`/`__import__`.

## Agent luôn im lặng — `run_output.json` rất tối giản (Bạn phải tự cài đặt quan sát)
Agent chỉ trả về duy nhất **câu trả lời + mã trạng thái**. Các dòng trong `run_output.json` chỉ chứa các trường: `qid, question, answer, status, session, turn, ts` — **không có độ trễ, không có số lượng token, không có lượt gọi tool, không có vết thực thi từng bước**. Đây là sự cố ý: để quan sát được độ trễ, chi phí, việc sử dụng tool, vòng lặp, drift chất lượng, và rò rỉ thông tin cá nhân (PII), bạn **bắt buộc phải tự xây dựng nó trong hàm `mitigate()`**.

Tin vui là: `call_next(question, conf)` sẽ trả về **đầy đủ** kết quả cho *bạn* — `{answer, status, steps, trace, meta:{latency_ms, usage, model, tools_used, ...}}`. Bạn có thể ghi lại bất cứ thông tin nào mình cần tại đây:
```python
import time
def mitigate(call_next, question, config, context):
    t0 = time.time()
    r = call_next(question, config)
    meta = r.get("meta", {})
    # Observability của BẠN — nơi duy nhất chứa các tín hiệu này:
    # logger.log_event("CALL", {"qid": context["qid"], "wall_ms": int((time.time()-t0)*1000),
    #   "latency_ms": meta.get("latency_ms"), "usage": meta.get("usage"),
    #   "tools": meta.get("tools_used"), "steps": r.get("steps"), "trace": r.get("trace")})
    return r
```
Trình mô phỏng (sim) cũng ghi một khối mã hóa có chữ ký **`sealed`** vào tệp `run_output.json` — đây là bản sao chống làm giả của *scorer* dùng để đo lường các chỉ số của binary (độ trễ/token/công cụ), và nó **không** phải là khả năng quan sát của bạn. Việc sửa đổi hoặc xóa nó đi sẽ khiến điểm số về độ trễ/chi phí của bạn bị đặt về 0.

## Lưu ý (v6)
Agent chạy trên một **LLM thật** và hoạt động **dựa trên prompt** — hiệu quả tối ưu lớn nhất đến từ việc viết lại `solution/prompt.txt` (và các knob cấu hình trong config như `temperature`, `self_consistency`, `tool_budget`), chứ không chỉ riêng ở wrapper. Tuy nhiên, wrapper hiện tại là **bắt buộc để có khả năng quan sát** (cách duy nhất để thấy độ trễ/chi phí/trace/drift/PII) bên cạnh các chức năng bổ sung như retry/cache/redact/sanitize. Lượt chạy đầy đủ là đồng thời (`--concurrency`), do đó hãy đảm bảo hàm `mitigate()` an toàn luồng (thread-safe, bảo vệ `context["cache"]` bằng `context["cache_lock"]`).
