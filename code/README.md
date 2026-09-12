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

## Changelog

**Fix: multi-stream (category, direction) buckets in `RecurrenceDetector`.**
The 5% tolerance band used to decide whether a `(category, direction)` bucket
recurs was previously anchored on the single most-recent event in that
bucket. When a bucket actually contains two genuinely different sub-streams
posting under the same category — e.g. a fixed monthly "Base salary" credit
mixed with a variable "Performance/Sales commission" credit, both filed under
`category=salary, direction=credit` — anchoring on whichever one happened
most recently could pull in the volatile stream and cause the *whole bucket*
to fail the 3-month recurrence test, silently dropping a real, stable income
stream from the 90-day forecast. Verified against `dataset/sample_requests.csv`:
this was the dominant driver of wrong `amount_safe_to_pay` values, not the
salary-termination edge case fixed in an earlier pass.

The detector now tries every event in the bucket as a candidate tolerance
anchor and keeps the largest resulting cluster that still spans 3+ distinct
months, before falling back to the existing frequency-based / 90-day-average
heuristics. This is applied uniformly (it is not a keyword or user-specific
patch) and improved agreement with the 25 labeled `sample_requests.csv` rows
across the board — several requests now match ground truth exactly.

**Known remaining gaps** (as of this fix, checked against `sample_requests.csv`):
`request_04`, `request_05`, `request_10`, `request_13`, `request_15`,
`request_20`, and `request_25` still diverge from ground truth by more than a
few percent. Spot-checking suggests the residual error is not from recurrence
detection anymore but from some other source — needs further per-user tracing
(possible remaining candidates: how a stopped/reduced spending change should
interact with the baseline pre-change forecast, and whether some monthly
category's projected day-of-month should shift when its historical cadence
isn't perfectly regular). This is flagged honestly rather than papered over;
treat the current numbers as improved, not fully verified.
