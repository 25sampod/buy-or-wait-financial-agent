import csv
import datetime
import os
import sys

# Ensure code is importable
sys.path.insert(0, os.path.abspath('code'))
import main as M

def run_sample_check():
    data_dir = os.path.join(M.REPO_ROOT, 'dataset')
    sample_path = os.path.join(data_dir, 'sample_requests.csv')
    
    if not os.path.isfile(sample_path):
        print(f"Sample requests file not found: {sample_path}")
        return

    # Load samples
    sample_rows = []
    with open(sample_path) as f:
        for r in csv.DictReader(f):
            sample_rows.append(r)

    # Initialize data loader for dataset
    loader = M.DataLoader(data_dir)
    llm = M.LLMClient()
    if '--live' not in sys.argv:
        llm.client = None  # Ensure deterministic offline sample checking
    loader.load_all(llm=llm)

    mismatches = 0
    field_mismatch_counts = {
        'amount_safe_to_pay': 0,
        'affordability_status': 0,
        'recommended_payment_method': 0,
        'payment_plan': 0,
        'earliest_date_for_full_payment': 0,
        'spending_changes_needed': 0
    }
    
    diffs = []

    for expected in sample_rows:
        req_id = expected['request_id']
        req = [r for r in loader.requests if r.request_id == req_id]
        if not req:
            req = [M.Request(**expected)]
        req = req[0]
        profile = loader.profiles.get(req.user_id)
        if not profile:
            print(f"Profile missing for user {req.user_id}")
            continue

        user_msgs = loader.messages.get(req.user_id, [])
        insights = llm.interpret_messages(req.user_id, user_msgs)
        user_events = [e for e in loader.events if e.user_id == req.user_id]
        
        detector = M.RecurrenceDetector(user_events, req.request_date)
        recurring = detector.detect()

        salaries = [e for e in user_events if e.category == 'salary' and e.status in ('scheduled', 'settled')]
        salary_ended = (insights.salary_update and insights.salary_update.is_ended) or M.is_income_terminated(user_events, 'salary')
        if salaries and not salary_ended:
            latest_sal = sorted(salaries, key=lambda x: x.date)[-1]
            sal_amt = latest_sal.amount or 0.0
            sal_day = latest_sal.date.day
            if insights.salary_update:
                if insights.salary_update.new_amount is not None:
                    sal_amt = insights.salary_update.new_amount
                if insights.salary_update.new_day is not None:
                    sal_day = insights.salary_update.new_day
            if sal_amt > 0 and not any(r.category == 'salary' for r in recurring):
                recurring.append(M.RecurringEvent('salary', 'credit', sal_amt, sal_day, latest_sal))

        stop_cats = set()
        reduce_cats = {}
        for eu in insights.expense_updates:
            if eu.percentage_increase is not None:
                for r in recurring:
                    if r.category == eu.category:
                        reduce_cats[r.category] = r.amount * (1.0 + eu.percentage_increase / 100.0)

        forecaster = M.BalanceForecaster(profile.current_available_balance, req.request_date)
        forecaster.add_recurring(recurring, stop_cats, reduce_cats)
        forecaster.add_pending_and_scheduled(user_events, exclude_categories={'salary'})
        daily_balances = forecaster.simulate()

        safe_amt = M.compute_safe_amount(daily_balances, profile.minimum_balance_to_keep, req.requested_amount)
        earliest = M.find_earliest_date(daily_balances, profile.minimum_balance_to_keep, req.requested_amount, req.request_date)

        opts = loader.payment_options.get(req.request_id, [])
        plan = M.select_payment_plan(profile, req, safe_amt, earliest, opts, daily_balances)
        changes = []

        if not plan or plan.status == 'affordable_later':
            ch_plan, ch_safe, ch_earliest, ch_list = M.evaluate_spending_changes(profile, req, recurring, user_events, opts, llm)
            if ch_plan:
                plan = ch_plan
                changes = ch_list

        target_plan = plan or M.Plan(method='not_recommended', status='not_affordable', payments=[], total=0)
        if target_plan.status == 'not_affordable':
            earliest_str = ''
        elif target_plan.status == 'affordable_now':
            earliest_str = M.format_date(req.request_date)
        else:
            earliest_str = M.format_date(earliest) if earliest else ''

        pred_safe_str = M.format_safe_amount(safe_amt)
        pred = {
            'amount_safe_to_pay': pred_safe_str,
            'affordability_status': target_plan.status,
            'recommended_payment_method': target_plan.method,
            'payment_plan': M.format_plan_str(target_plan),
            'earliest_date_for_full_payment': earliest_str,
            'spending_changes_needed': M.format_changes_str(changes),
        }

        row_diffs = {}
        for field in field_mismatch_counts:
            exp_val = expected[field].strip()
            pred_val = str(pred[field]).strip()
            
            if field == 'amount_safe_to_pay':
                try:
                    if abs(float(exp_val) - float(pred_val)) > 0.5:
                        field_mismatch_counts[field] += 1
                        row_diffs[field] = f"exp={exp_val} vs pred={pred_val}"
                except ValueError:
                    if exp_val != pred_val:
                        field_mismatch_counts[field] += 1
                        row_diffs[field] = f"exp={exp_val} vs pred={pred_val}"
            else:
                if exp_val != pred_val:
                    field_mismatch_counts[field] += 1
                    row_diffs[field] = f"exp={exp_val} vs pred={pred_val}"

        if row_diffs:
            mismatches += 1
            diffs.append((req_id, row_diffs))

    print(f"Total sample rows: {len(sample_rows)}")
    print(f"Rows with at least one mismatch: {mismatches}/{len(sample_rows)}")
    print("Field-level mismatch counts:")
    for f, cnt in field_mismatch_counts.items():
        print(f"  {f:30}: {cnt}")
    print("\nDetailed diffs:")
    for rid, rd in diffs:
        print(f"  [{rid}]:")
        for f, d in rd.items():
            print(f"      {f}: {d}")

if __name__ == '__main__':
    run_sample_check()
