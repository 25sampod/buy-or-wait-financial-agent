# LLM Token Usage and Cost Report

This report summarizes the model calls, token consumption, and cost analysis for the final full-dataset evaluation run of the **Buy or Wait?** financial agent.

## Model Summary

- **Provider**: Azure OpenAI / Hybrid Architecture
- **Primary Model**: GPT-5 Nano / GPT-4o Multimodal Vision & Reasoning
- **Execution Mode**: Batch pre-processing for multimodal assets + deterministic financial simulation core + explanation generation

## Quantitative Metrics

| Metric | Total | Average per Request (250 Requests) |
| :--- | :--- | :--- |
| **Model Invocations** | 481 calls | 1.92 calls/req |
| **Input Tokens** | 230,880 tokens | 923.5 tokens/req |
| **Output Tokens** | 45,695 tokens | 182.8 tokens/req |
| **Total Tokens** | 276,575 tokens | 1106.3 tokens/req |
| **Estimated Cost (USD)** | $0.0620 | $0.0002/req |

## Component Breakdown

1. **Image Amount Extraction**: 16 calls on visual invoice, payslip, and bill artifacts using multimodal vision.
2. **Message Interpretation**: 215 structured JSON extractions across user communication threads for salary updates and expense amendments.
3. **Decision Explanations**: 250 grounded natural language explanations generated per output decision.
4. **Deterministic Core**: Zero LLM tokens spent on financial simulation, calendar recurrence detection, and plan ranking (guaranteeing exact mathematical reproducibility).
