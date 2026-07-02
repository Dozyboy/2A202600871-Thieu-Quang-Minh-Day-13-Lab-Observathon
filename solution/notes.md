# Sổ tay Chẩn đoán Lỗi (Diagnosis scratchpad)

Dưới đây là bảng tổng hợp các triệu chứng chẩn đoán, nguyên nhân gốc rễ và các giải pháp đã triển khai (cấu hình trong `config.json` hoặc mã hóa trong `wrapper.py`) để sửa chữa toàn bộ 11 lớp lỗi trong bài Lab Observathon.

| Mã lỗi | Triệu chứng (Symptom) | Yêu cầu bị ảnh hưởng | Nguyên nhân gốc rễ (Root Cause) | Khắc phục bằng Config? | Khắc phục bằng Wrapper? |
|---|---|---|---|---|---|
| **F1** (latency_spike) | Độ trễ P95 tăng vọt khi chạy mô phỏng. | Các yêu cầu RAG mất nhiều thời gian. | Hệ thống truy xuất bị chậm do truy vấn cơ sở dữ liệu lớn. | Bật `cache` | Thêm bộ nhớ đệm (caching) luồng an toàn. |
| **F2** (error_spike) | Lỗi 500 hoặc `wrapper_error` ngẫu nhiên. | Các cuộc gọi tool bị timeout hoặc ngắt kết nối. | Vector Store bị quá tải dưới tải trọng lớn. | Bật `retry` | Cài đặt cơ chế auto-retry với exponential backoff. |
| **F3** (cost_blowup) | Chi phí token đầu ra tăng đột biến. | Các câu trả lời của LLM quá dài và lan man. | LLM diễn giải dông dài hoặc lặp đi lặp lại lý luận. | Đặt `max_completion_tokens` | Rút ngắn hướng dẫn hệ thống trong prompt. |
| **F4** (infinite_loop) | Yêu cầu bị treo hoặc trả về lỗi `loop`. | LLM lặp lại vô hạn một vài tool gọi. | Thiếu điều kiện dừng rõ ràng khi kết quả tool không đổi. | Bật `loop_guard` và giới hạn `max_steps` | Thêm logic dừng khẩn cấp. |
| **F5** (pii_leak) | Email hoặc SĐT của khách hàng bị lặp lại. | Các yêu cầu chứa thông tin liên lạc của khách. | LLM sao chép nguyên văn thông tin PII vào câu trả lời cuối. | Bật `redact_pii` | Thêm bộ lọc Regex tự động làm sạch PII trước khi trả về. |
| **F6** (arithmetic_error) | Tính sai tổng tiền hoặc phần trăm giảm giá. | Đơn hàng áp dụng coupon hoặc phí ship. | LLM ước lượng kết quả thay vì tính chia lấy nguyên chuẩn xác. | Giảm `temperature` xuống 0.2 | Tự động tính toán lại số học chuẩn bằng Python. |
| **F7** (tool_overuse) | Số lần gọi tool rất cao cho mỗi session. | Các câu hỏi truy vấn thông tin tồn kho. | Agent gọi đi gọi lại một tool nhiều lần để "chắc chắn". | Giới hạn `tool_budget` | Chỉ thị gọi tool song song 1 lần duy nhất trong prompt. |
| **F8** (fabrication) | Tính tổng tiền cho sản phẩm đã hết hàng. | Đơn hàng mua sản phẩm có `in_stock: false`. | LLM tự ý bịa giá để hoàn thành đơn hàng thay vì từ chối. | Yêu cầu từ chối trong prompt | Ép trạng thái `refusal` và định dạng từ chối chuẩn hóa. |
| **F9** (tool_failure) | Lỗi tính ship cho các thành phố có dấu. | Giao hàng đến các thành phố như Hà Nội, Đà Nẵng. | Không tương thích mã hóa ký tự Unicode giữa LLM và Database. | Bật `normalize_unicode` | Không cần (đã xử lý bằng cấu hình chuẩn). |
| **F10** (quality_drift) | Chất lượng trả lời giảm dần ở cuối session. | Các lượt hội thoại thứ 8-12 trở đi. | Bộ nhớ ngữ cảnh bị tích tụ nhiễu qua nhiều lượt chat. | Cấu hình `session_drift_rate` | Không cần (xử lý bằng cấu hình). |
| **F11** (prompt_injection) | Agent làm theo giá/coupon ảo trong ghi chú. | Đơn hàng có kèm ghi chú `GHI CHU KHACH: ...`. | System prompt coi ghi chú là chỉ thị thực thi thay vì dữ liệu tĩnh. | Không cần | Dùng regex bóc tách làm sạch ghi chú trước khi đưa vào LLM. |
