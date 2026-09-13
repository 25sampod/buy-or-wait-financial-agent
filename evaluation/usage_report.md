# LLM Token Usage and Cost Report

This report summarizes the model calls, token consumption, and cost analysis for the evaluation run of the **Buy or Wait?** financial agent.

## Model Summary

- **Active Provider**: Azure OpenAI (gpt-5-nano)
- **Supported Providers**: Anthropic Claude, OpenAI, Azure OpenAI, Google Gemini
- **Execution Mode**: Live API execution (Azure OpenAI (gpt-5-nano))

## Quantitative Metrics

| Metric | Total | Average per Request (250 Requests) |
| :--- | :--- | :--- |
| **Model Invocations (Live)** | 464 calls | 1.86 calls/req |
| **Cache Hits** | 214 hits | 0.86 hits/req |
| **Input Tokens** | 104,775 tokens | 419.1 tokens/req |
| **Output Tokens** | 574,745 tokens | 2299.0 tokens/req |
| **Total Tokens** | 679,520 tokens | 2718.1 tokens/req |
| **Estimated Cost (USD)** | $0.3606 | $0.0014/req |

## Evaluation Notes

This evaluation run executed live API calls using active provider: Azure OpenAI (gpt-5-nano).

## Component Breakdown

1. **Image Amount Extraction**: 16 multimodal vision extractions from invoices, payslips, and receipts.
2. **Message Interpretation**: 198 structured audits across communication logs resolving payment confirmations, salary amendments, and debit cancellations.
3. **Decision Explanations**: 250 grounded natural language explanations generated for every evaluation request.
4. **Deterministic Core**: Zero LLM tokens spent on financial simulation, recurrence detection, and plan optimization, guaranteeing 100% mathematical precision and balance safety.
