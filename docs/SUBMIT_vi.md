# Nộp bài

Agent chạy trên một **LLM thật** — hãy thiết lập key hoặc endpoint local trước:
```bash
export OPENAI_API_KEY=sk-...                 # Đám mây (model mặc định gpt-5.4-nano)
# HOẶC chạy local miễn phí: chạy Ollama/llama.cpp và thiết lập provider:"local" trong config.json + LOCAL_BASE_URL
```

1. **Tự kiểm tra** khung nộp bài (chỉ dùng thư viện chuẩn, không cần key):
   ```bash
   python harness/selfcheck.py
   ```
2. **Chạy mô phỏng** cho giai đoạn hiện tại:
   ```bash
   ./bin/<phase>/observathon-sim --config solution/config.json --wrapper solution/wrapper.py \
       --out run_output.json --concurrency 8
   #   <phase> = practice | public | private
   #   macOS lần chạy đầu tiên: xattr -dr com.apple.quarantine bin/<phase>/*
   ```
3. **Chấm điểm** kết quả chạy (giai đoạn public/private):
   ```bash
   ./bin/<phase>/observathon-score --run run_output.json --findings solution/findings.json \
       --team <TEAM> --out score.json
   ```
4. **Commit & push** thư mục `solution/` (bao gồm config.json, prompt.txt, examples.json, wrapper.py, findings.json, cùng nhật ký logs/traces của bạn) + `run_output.json` + `score.json`:
   ```bash
   git add solution/ run_output.json score.json && git commit -m "<tên_đội> <giai_đoạn>" && git push
   ```

## Binary theo Hệ điều hành (`bin/<phase>/`)
| Hệ điều hành / Kiến trúc | Tệp |
|---|---|
| macOS (Apple Silicon, M1+) | `observathon-sim` / `observathon-score` (arm64) |
| Windows | `observathon-sim.exe` / `observathon-score.exe` |
| Linux | `observathon-sim` / `observathon-score` (x86_64) |

(macOS Intel không được dựng sẵn — Apple Silicon, Windows và Linux được cung cấp sẵn; đối với Intel, hãy chạy từ mã nguồn bằng Python + thư viện `openai`.)

## Các giai đoạn
Giai đoạn practice bắt đầu ở T0 → public **sim** ở T+1h, **score** ở T+2h → private **sim** ở T+3h, **score** ở T+3.5h.
Giai đoạn **private** bổ sung một bộ dữ liệu ẩn, được diễn đạt lại + đòn tấn công **prompt injection**. Chỉ cần push kết quả private của bạn một lần duy nhất khi hoàn thành.
