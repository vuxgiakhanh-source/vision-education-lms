import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from review_lab import attendance_rate, bad_attendance_rate
from renewal_reference import Loan, renew_loan


class ReportReviewTests(unittest.TestCase):
    def test_original_counterexample(self):
        statuses = ['present', 'late', 'absent', 'excused', None]
        self.assertEqual(bad_attendance_rate(statuses), 20.0)
        self.assertEqual(attendance_rate(statuses), 66.67)

    def test_no_eligible_data_is_not_zero_percent(self):
        for statuses in ([], [None], ['excused', None]):
            with self.subTest(statuses=statuses):
                self.assertIsNone(attendance_rate(statuses))

    def test_all_absent_and_all_attended(self):
        self.assertEqual(attendance_rate(['absent', 'absent']), 0.0)
        self.assertEqual(attendance_rate(['present', 'late']), 100.0)

    def test_unknown_data_is_rejected(self):
        with self.assertRaises(ValueError):
            attendance_rate(['present', 'unknown'])

    def test_input_is_not_modified(self):
        statuses = ['late', None, 'absent', 'excused']
        before = statuses.copy()
        self.assertEqual(attendance_rate(statuses), 50.0)
        self.assertEqual(statuses, before)


class RenewalTransferTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 17, 8, 0, tzinfo=timezone.utc)
        self.loan = Loan(10, 2, self.now + timedelta(days=3))

    def test_extends_from_due_date_and_keeps_original(self):
        renewed = renew_loan(self.loan, 2, False, self.now)
        self.assertEqual(renewed.due_at, self.loan.due_at + timedelta(days=7))
        self.assertEqual(renewed.renewals, 1)
        self.assertEqual(self.loan.renewals, 0)

    def test_exact_due_time_is_already_too_late(self):
        with self.assertRaises(ValueError):
            renew_loan(self.loan, 2, False, self.loan.due_at)

    def test_wrong_borrower(self):
        with self.assertRaises(PermissionError):
            renew_loan(self.loan, 99, False, self.now)

    def test_returned_max_renewals_or_queue_each_block(self):
        cases = [(replace(self.loan, returned=True), False),
                 (replace(self.loan, renewals=2), False),
                 (self.loan, True)]
        for loan, waiting in cases:
            with self.subTest(loan=loan, waiting=waiting):
                with self.assertRaises(ValueError):
                    renew_loan(loan, 2, waiting, self.now)

    def test_naive_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            renew_loan(self.loan, 2, False, datetime(2026, 10, 17, 8, 0))


if __name__ == '__main__':
    unittest.main()
