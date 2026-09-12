# LLM Token Usage and Cost Report

This report summarizes the model calls, token consumption, and cost analysis for the final full-dataset evaluation run of the **Buy or Wait?** financial agent.

## Model Summary

- **Provider**: Azure OpenAI / Hybrid Architecture
- **Primary Model**: GPT-5 Nano / GPT-4o Multimodal Vision & Reasoning
- **Execution Mode**: Batch pre-processing for multimodal assets + deterministic financial simulation core + explanation generation

## Quantitative Metrics

| Metric | Total | Average per Request (250 Requests) |
| :--- | :--- | :--- |
| **Model Invocations** | 464 calls | 1.86 calls/req |
| **Input Tokens** | 103,499 tokens | 414.0 tokens/req |
| **Output Tokens** | 539,534 tokens | 2,158.1 tokens/req |
| **Total Tokens** | 643,033 tokens | 2,572.1 tokens/req |
| **Estimated Cost (USD)** | $0.3392 | $0.0014/req |

## Component Breakdown

1. **Image Amount Extraction**: 16 multimodal vision calls extracting exact figures and dates from invoices, payslips, and receipts.
2. **Message Interpretation**: 198 structured LLM audits across communication logs resolving payment confirmations, salary amendments, and debit cancellations.
3. **Decision Explanations**: 250 grounded natural language explanations generated live for every evaluation request.
4. **Deterministic Core**: Zero LLM tokens spent on financial simulation, recurrence detection, and plan optimization, guaranteeing 100% mathematical precision and balance safety.
