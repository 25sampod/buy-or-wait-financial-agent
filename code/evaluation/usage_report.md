# LLM Token Usage and Cost Report

This report summarizes the model calls, token consumption, and cost analysis for the evaluation run of the **Buy or Wait?** financial agent.

## Model Summary

- **Provider**: Azure OpenAI / Hybrid Architecture
- **Primary Model**: GPT-5 Nano / GPT-4o Multimodal Vision & Reasoning
- **Execution Mode**: Offline cached evaluation run (code/ai_cache.json)

## Quantitative Metrics

| Metric | Total | Average per Request (250 Requests) |
| :--- | :--- | :--- |
| **Model Invocations (Live)** | 0 calls | 0.00 calls/req |
| **Cache Hits** | 464 hits | 1.86 hits/req |
| **Input Tokens** | 0 tokens | 0.0 tokens/req |
| **Output Tokens** | 0 tokens | 0.0 tokens/req |
| **Total Tokens** | 0 tokens | 0.0 tokens/req |
| **Estimated Cost (USD)** | $0.0000 | $0.0000/req |

## Evaluation Notes

This evaluation run used pre-computed AI inferences from code/ai_cache.json (464 cached responses: 16 image OCR extractions, 198 message interpretations, 250 decision explanations). No live API calls were made during this run. The original generation run used Azure OpenAI gpt-5-nano / gpt-4o.

## Component Breakdown

1. **Image Amount Extraction**: 16 multimodal vision extractions from invoices, payslips, and receipts.
2. **Message Interpretation**: 198 structured LLM audits across communication logs resolving payment confirmations, salary amendments, and debit cancellations.
3. **Decision Explanations**: 250 grounded natural language explanations generated for every evaluation request.
4. **Deterministic Core**: Zero LLM tokens spent on financial simulation, recurrence detection, and plan optimization, guaranteeing 100% mathematical precision and balance safety.
