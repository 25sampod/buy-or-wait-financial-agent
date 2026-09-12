# HackerRank Orchestrate - Buy or Wait?

## Architecture Overview

This project uses a hybrid architecture combining deterministic financial modeling with an LLM for unstructured data. The pipeline consists of 10 components:
1. **Data Loading & Linked Event Resolution**: Cleans historical data and resolves superseded transactions.
2. **Exchange Rate Conversion**: Normalizes foreign currencies to home currency.
3. **Recurrence Detection**: Hybrid calendar+frequency system to predict future cash flows.
4. **Balance Forecasting**: Day-by-day simulation of the user's available balance over 90 days.
5. **Computing `amount_safe_to_pay`**: O(1) closed-form calculation of the safe payment amount based on the 90-day minimum forecast.
6. **Finding `earliest_date_for_full_payment`**: O(N) suffix-min scan to find the earliest safe date.
7. **Payment Plan Selection**: Generates eligible candidates (full, partial, wait, installments) and ranks them strictly on cost/timing.
8. **Spending Changes**: If no plans are affordable, attempts greedy reductions on flexible categories.
9. **Message Interpretation**: LLM extracts overrides for salary/expenses via structured JSON output.
10. **Image Extraction & Explanations**: LLM extracts missing amounts from images and generates natural language explanations.

## How to Run

1. Create a `.env` file in the root directory (for local testing):
   ```
   AZURE_OPENAI_ENDPOINT=<your_endpoint>
   AZURE_OPENAI_API_KEY=<your_api_key>
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   ```
2. Install dependencies:
   ```bash
   pip install -r code/requirements.txt
   ```
3. Run the main script:
   ```bash
   python3 code/main.py
   ```
   To run and generate the final submission zip (with `evaluation/usage_report.md`):
   ```bash
   python3 code/main.py --package
   ```

## Design Notes

**RecurrenceDetector**: Designed as a hybrid calendar and frequency detector because data shows a strict 5% tolerance is needed to isolate true fixed contracts. If a category misses the calendar threshold due to variance, it falls back to a frequency-based interval detector to prevent missing highly variable utility/dining bills.

**BalanceForecaster**: Structured as a strict 91-day integer array (0 to 90) rather than a continuous time-series. This allows extremely fast O(N) operations like the suffix-min scan for finding the earliest safe date, avoiding O(N^2) trial-and-error simulation.
