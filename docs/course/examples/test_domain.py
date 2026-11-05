"""Test lời giải học tập. Không chạm database hoặc ứng dụng thật."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from domain import (
    AccessDenied, Actor, AlreadySubmitted, Assignment, AssignmentNotFound,
    AssignmentStatus, AssignmentUnavailable, DeadlinePassed, InvalidAnswer,
    MemorySubmissionRepository, Role, SubmitService, grade_numeric,
    parse_decimal_answer, validate_score,
)


class SubmitServiceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        self.due = self.now + timedelta(hours=1)
        self.repository = MemorySubmissionRepository()
        self.repository.assignments[10] = Assignment(10, 7, AssignmentStatus.PUBLISHED, self.due)
        self.repository.memberships.add((7, 2))
        self.student = Actor(2, Role.STUDENT)
        self.service = SubmitService(self.repository)

    def submit(self, answer='A', now=None, actor=None, assignment_id=10):
        return self.service.submit(
            actor or self.student, assignment_id, answer,
            self.now if now is None else now,
        )

    def test_success_saves_normalized_answer_and_owner(self):
        result = self.submit('  A  ')
        self.assertEqual((result.assignment_id, result.student_id, result.answer), (10, 2, 'A'))
        self.assertEqual(result.submitted_at, self.now)
        self.assertEqual(len(self.repository.submissions), 1)

    def test_empty_answer_does_not_save(self):
        with self.assertRaises(InvalidAnswer):
            self.submit(' \n\t ')
        self.assertEqual(self.repository.submissions, {})

    def test_too_long_answer_does_not_save(self):
        with self.assertRaises(InvalidAnswer):
            self.submit('a' * 10_001)
        self.assertEqual(self.repository.submissions, {})

    def test_maximum_length_is_accepted(self):
        self.assertEqual(len(self.submit('a' * 10_000).answer), 10_000)

    def test_teacher_cannot_submit_as_student(self):
        with self.assertRaises(AccessDenied):
            self.submit(actor=Actor(2, Role.TEACHER))
        self.assertEqual(self.repository.submissions, {})

    def test_inactive_student_cannot_submit(self):
        with self.assertRaises(AccessDenied):
            self.submit(actor=Actor(2, Role.STUDENT, active=False))
        self.assertEqual(self.repository.submissions, {})

    def test_outside_class_is_denied(self):
        with self.assertRaises(AccessDenied):
            self.submit(actor=Actor(99, Role.STUDENT))
        self.assertEqual(self.repository.submissions, {})

    def test_missing_assignment(self):
        with self.assertRaises(AssignmentNotFound):
            self.submit(assignment_id=999)

    def test_draft_is_unavailable(self):
        self.repository.assignments[10] = replace(
            self.repository.assignments[10], status=AssignmentStatus.DRAFT,
        )
        with self.assertRaises(AssignmentUnavailable):
            self.submit()
        self.assertEqual(self.repository.submissions, {})

    def test_closed_is_unavailable_for_new_submission(self):
        self.repository.assignments[10] = replace(
            self.repository.assignments[10], status=AssignmentStatus.CLOSED,
        )
        with self.assertRaises(AssignmentUnavailable):
            self.submit()

    def test_exact_deadline_is_inclusive(self):
        self.assertEqual(self.submit(now=self.due).submitted_at, self.due)

    def test_after_deadline_rejected_without_write(self):
        with self.assertRaises(DeadlinePassed):
            self.submit(now=self.due + timedelta(microseconds=1))
        self.assertEqual(self.repository.submissions, {})

    def test_no_deadline_accepts_new_submission(self):
        self.repository.assignments[10] = replace(self.repository.assignments[10], due_at=None)
        self.assertEqual(self.submit(now=self.now + timedelta(days=100)).student_id, 2)

    def test_naive_clock_rejected(self):
        with self.assertRaises(ValueError):
            self.submit(now=datetime(2026, 11, 1, 12))

    def test_naive_deadline_rejected(self):
        with self.assertRaises(ValueError):
            Assignment(20, 7, AssignmentStatus.PUBLISHED, datetime(2026, 11, 1))

    def test_retry_returns_original_object_and_timestamp(self):
        first = self.submit('A')
        retry = self.submit(' A ', now=self.now + timedelta(minutes=5))
        self.assertIs(retry, first)
        self.assertEqual(retry.submitted_at, self.now)
        self.assertEqual(len(self.repository.submissions), 1)

    def test_retry_after_deadline_still_returns_saved_submission(self):
        first = self.submit()
        retry = self.submit(now=self.due + timedelta(hours=1))
        self.assertEqual(retry.id, first.id)
        self.assertEqual(retry.submitted_at, first.submitted_at)

    def test_retry_after_closing_does_not_create_new_submission(self):
        first = self.submit()
        self.repository.assignments[10] = replace(
            self.repository.assignments[10], status=AssignmentStatus.CLOSED,
        )
        self.assertIs(self.submit(), first)
        self.assertEqual(len(self.repository.submissions), 1)

    def test_changed_answer_conflicts_and_preserves_original(self):
        original = self.submit('A')
        with self.assertRaises(AlreadySubmitted):
            self.submit('B')
        self.assertEqual(self.repository.find_submission(10, 2), original)

    def test_different_students_have_different_submissions(self):
        self.repository.memberships.add((7, 3))
        first = self.submit()
        other = self.submit(actor=Actor(3, Role.STUDENT))
        self.assertNotEqual(first.id, other.id)
        self.assertEqual(len(self.repository.submissions), 2)

    def test_fake_instances_do_not_share_data(self):
        self.submit()
        self.assertEqual(MemorySubmissionRepository().submissions, {})


class GradeTests(unittest.TestCase):
    def test_zero_is_a_valid_score(self):
        self.assertEqual(validate_score(Decimal('0')), Decimal('0'))

    def test_ten_is_a_valid_score(self):
        self.assertEqual(validate_score(Decimal('10')), Decimal('10'))

    def test_out_of_range_or_nonfinite_scores_are_rejected(self):
        for value in ['-0.01', '10.01', 'NaN', 'Infinity']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_score(Decimal(value))

    def test_float_is_not_silently_accepted(self):
        with self.assertRaises(TypeError):
            validate_score(0.1)

    def test_equivalent_decimal_strings(self):
        self.assertEqual(grade_numeric('0.5', ' 0.50 '), 1)
        self.assertEqual(grade_numeric('0', '-0.0'), 1)

    def test_wrong_numeric_value(self):
        self.assertEqual(grade_numeric('0.5', '0.6'), 0)

    def test_invalid_numeric_formats(self):
        for value in ['', 'NaN', 'Infinity', '1e3', '1/2', '0,5', '.5', '1' * 101]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_decimal_answer(value)


if __name__ == '__main__':
    unittest.main()
