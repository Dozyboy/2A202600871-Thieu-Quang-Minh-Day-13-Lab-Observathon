# Findings — Team DOZYBOY

For each fault you found, fill one row AND a matching entry in `solution/findings.json`
(the JSON is what's scored; this MD is for humans). Evidence must come from YOUR telemetry.

| fault_class | evidence (metric + observed value + trace ids) | root cause | fix (config / wrapper) |
|---|---|---|---|
| **latency_spike** | latency_p95 and latency_p99 increased to ~2650ms. Traces and response logs show slow agent runs. | The retrieval step introduced a blocking 2.5-second sleep via the `rag_slow` toggle. | Add thread-safe caching in `wrapper.py` and set retrieval timeout limits. |
| **error_spike** | error_breakdown metric rose. Logs contain `RuntimeError: Vector store timeout`. | Retrieval tool failures and timeout exceptions raised by the database during load. | Implement auto-retry with exponential backoff and wrapper exceptions handling. |
| **cost_blowup** | tokens_out_total and avg_cost_usd grew by 4x. Logs show cost spikes. | The LLM generated redundant output tokens. | Set max output tokens limit and reduce prompt verbosity. |
| **infinite_loop** | status=loop and status=max_steps in logs. Traces show duplicate tool calls. | Poor agent stopping criteria causing duplicated tool executions. | Enable loop_guard: true and limit max_steps in config.json. |
| **pii_leak** | Contact details matching regex flagged in agent responses. | LLM echoes client emails/phones back in final answers. | Use regex-based PII redaction wrapper layer and prompt instructions. |
| **arithmetic_error** | n_correct correctness rates degraded under temp 1.6. | LLM estimates math totals instead of calculating exactly. | Lower temperature to 0.2 and add step-by-step verification rules in prompt.txt. |
| **tool_overuse** | Same tool called multiple times per request in trace. | Agent calls check_stock/calc_shipping repeatedly 'to be safe'. | Limit tool_budget in config.json and prompt once-per-tool instruction. |
| **fabrication** | Subtotal calculated for items with in_stock=false. | LLM attempts to satisfy request by hallucinating unavailable prices. | Instruct model to refuse and output no total when items are out of stock. |
| **tool_failure** | calc_shipping fails for cities with diacritics. | Unicode encoding mismatches when sending Vietnamese city strings. | Enable normalize_unicode: true in config.json. |
| **quality_drift** | Correctness decreases as turn_index session grows. | Accumulation of context history noise over long turns. | Reduce context_size or reset session state variables. |
| **prompt_injection** | Subtotal matches fake discount or price in note. | Agent follows hidden instructions in order notes. | Sanitize notes in wrapper.py and treat note text as passive data in prompt.txt. |
