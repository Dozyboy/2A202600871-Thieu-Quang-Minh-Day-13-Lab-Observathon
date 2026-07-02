# Findings — Team DOZYBOY

For each fault you found, fill one row AND a matching entry in `solution/findings.json`
(the JSON is what's scored; this MD is for humans). Evidence must come from YOUR telemetry.

| fault_class | evidence (metric + observed value + trace ids) | root cause | fix (config / wrapper) |
|---|---|---|---|
| **latency_spike** | latency_p95 and latency_p99 increased to ~2650ms. Traces and response logs show slow agent runs. | The retrieval step introduced a blocking 2.5-second sleep via the `rag_slow` toggle. | Add thread-safe caching in `wrapper.py` and set retrieval timeout limits. |
| **error_spike** | error_breakdown metric rose. Logs contain `RuntimeError: Vector store timeout`. | Retrieval tool failures and timeout exceptions raised by the database during load. | Implement auto-retry with exponential backoff and error boundary handling in `wrapper.py`. |
| **cost_blowup** | tokens_out_total and avg_cost_usd grew by 4x. Logs show cost spikes. | The LLM generated redundant output tokens. | Set max output tokens limit and reduce prompt verbosity. |
