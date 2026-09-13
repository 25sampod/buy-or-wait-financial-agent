import unittest
import datetime
from main import (
    parse_date, FinancialEvent, resolve_linked_events,
    RecurringEvent, RecurrenceDetector, BalanceForecaster,
    compute_safe_amount, find_earliest_date, Plan, select_payment_plan,
    UserProfile, Request, PaymentOption
)

class TestLinkedEvents(unittest.TestCase):
    def test_linked_event_supersede(self):
        def make_event(id, parent, status, dir='debit'):
            return FinancialEvent(
                event_id=id, user_id='u1', event_type='expense', description='x',
                category='x', direction=dir, amount=100, currency='USD',
                event_date='2026-01-01', settlement_date='2026-01-01',
                status=status, linked_event_id=parent, flexibility='fixed',
                minimum_allowed_amount=None
            )
            
        e1 = make_event('parent1', None, 'cancelled')
        e2 = make_event('child1', 'parent1', 'settled')
        e3 = make_event('parent2', None, 'settled')
        e4 = make_event('child2', 'parent2', 'pending')
        e5 = make_event('parent3', None, 'settled')
        e6 = make_event('child3', 'parent3', 'settled')
        
        raw = [e1, e2, e3, e4, e5, e6]
        resolved = resolve_linked_events(raw)
        
        resolved_ids = {e.event_id for e in resolved}
        self.assertNotIn('parent1', resolved_ids)
        self.assertIn('child1', resolved_ids)
        self.assertNotIn('parent2', resolved_ids)
        self.assertIn('child2', resolved_ids)
        self.assertNotIn('parent3', resolved_ids)
        self.assertIn('child3', resolved_ids)

class TestRecurrence(unittest.TestCase):
    def test_calendar_recurrence(self):
        def make_event(d, amt):
            return FinancialEvent(
                event_id='e1', user_id='u1', event_type='expense', description='x',
                category='rent', direction='debit', amount=amt, currency='USD',
                event_date=d, settlement_date=d,
                status='settled', linked_event_id=None, flexibility='fixed',
                minimum_allowed_amount=None
            )
        e1 = make_event('2026-01-01', 1000)
        e2 = make_event('2026-02-01', 1000)
        e3 = make_event('2026-03-01', 1050)
        
        detector = RecurrenceDetector([e1, e2, e3], parse_date('2026-04-01'))
        recs = detector.detect()
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].category, 'rent')
        self.assertEqual(recs[0].amount, 1000)
        self.assertEqual(recs[0].day, 1)

class TestPlanRank(unittest.TestCase):
    def test_plan_ranking_tie_breaks(self):
        profile = UserProfile(
            user_id='u1', home_currency='USD', current_available_balance=1000,
            minimum_balance_to_keep=100, payment_methods_user_will_consider='installments|full_payment',
            max_installment_months=12
        )
        req = Request(
            request_id='r1', user_id='u1', request_date='2026-01-01', requested_amount=600,
            currency='USD', category='electronics', description='tv', desired_completion_date='2026-03-01',
            allows_partial_payment='false'
        )
        
        opt1 = PaymentOption(payment_option_id='opt1', request_id='r1', method='installments',
                             number_of_payments=3, days_between_payments=14, total_payable_amount=600)
        opt2 = PaymentOption(payment_option_id='opt2', request_id='r1', method='installments',
                             number_of_payments=3, days_between_payments=14, total_payable_amount=650)
                             
        best_plan = select_payment_plan(profile, req, amount_safe=1000, earliest_date=parse_date('2026-01-01'), options=[opt1, opt2])
        self.assertEqual(best_plan.method, 'full_payment')
        
        best_plan = select_payment_plan(profile, req, amount_safe=50, earliest_date=None, options=[opt1, opt2])
        self.assertEqual(best_plan.method, 'installments')
        self.assertEqual(best_plan.option_id, 'opt1')

class TestSafeAmount(unittest.TestCase):
    def test_formula(self):
        balances = [1000.0] * 5 + [700.0] * 10 + [1200.0] * 76
        safe = compute_safe_amount(balances, 200, 1000)
        self.assertEqual(safe, 500.0)

class TestImageProcessing(unittest.TestCase):
    def test_image_fallback_without_client(self):
        from main import LLMClient
        llm = LLMClient()
        llm.client = None
        amt = llm.extract_image_amount("dummy/path.png", "dummy_image")
        self.assertEqual(amt, 0.0, "Without API client, image extraction must return 0.0 safely without hardcoded tables")

class TestSalaryTermination(unittest.TestCase):
    def test_salary_termination_description(self):
        def make_salary(d, desc):
            return FinancialEvent(
                event_id=f"e_{d}", user_id="u_term", event_type="salary", description=desc,
                category="salary", direction="credit", amount=14740.0, currency="ZAR",
                event_date=d, settlement_date=d, status="settled", linked_event_id=None,
                flexibility="fixed", minimum_allowed_amount=None
            )
        e1 = make_salary("2025-06-15", "Payroll credit")
        e2 = make_salary("2025-07-15", "Payroll credit")
        e3 = make_salary("2025-08-15", "Payroll credit")
        e4 = make_salary("2025-09-15", "Payroll credit")
        e5 = make_salary("2025-10-15", "Final employer payroll")
        
        request_date = parse_date("2025-11-06")
        events = [e1, e2, e3, e4, e5]
        
        detector = RecurrenceDetector(events, request_date)
        recurring = detector.detect()
        
        self.assertFalse(any(r.category == 'salary' for r in recurring))
        
        from main import is_income_terminated
        self.assertTrue(is_income_terminated(events, 'salary'))
        
        forecaster = BalanceForecaster(1000.0, request_date)
        forecaster.add_recurring(recurring, set(), {})
        forecaster.add_pending_and_scheduled(events, exclude_categories={'salary'})
        
        salary_projected = [pe for pe in forecaster.events if pe.category == 'salary' and pe.date > parse_date("2025-10-15")]
        self.assertEqual(len(salary_projected), 0)

class TestUsageReport(unittest.TestCase):
    def test_offline_usage_report_metrics(self):
        import os
        from main import LLMClient, generate_usage_report, USAGE_REPORT_PATH
        llm = LLMClient()
        llm.live_calls_this_run = 0
        llm.total_input_tokens = 0
        llm.total_output_tokens = 0
        generate_usage_report(llm)
        
        self.assertTrue(os.path.exists(USAGE_REPORT_PATH))
        with open(USAGE_REPORT_PATH) as f:
            content = f.read()
            
        self.assertIn("Deterministic dataset execution", content)
        self.assertIn("0 calls", content)
        self.assertIn("$0.0000", content)

if __name__ == '__main__':
    unittest.main()
