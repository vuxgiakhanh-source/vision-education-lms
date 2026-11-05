"""G6: reproduce a wrong report, repair its rule, then verify the result."""
import sys


def bad_attendance_rate(statuses):
    present = 0
    for status in statuses:
        if status == 'present':
            present += 1
    return round(present * 100 / len(statuses), 2)


def attendance_rate(statuses):
    """Late counts as attended; exclude unmarked/excused from denominator."""
    attended = 0
    eligible = 0
    for status in statuses:
        if status is None or status == 'excused':
            continue
        if status not in ('present', 'late', 'absent'):
            raise ValueError('Unknown attendance status')
        eligible += 1
        if status in ('present', 'late'):
            attended += 1
    if eligible == 0:
        return None
    return round(attended * 100 / eligible, 2)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('bad', 'fixed'):
        raise SystemExit('Use: python review_lab.py bad|fixed')
    statuses = ['present', 'late', 'absent', 'excused', None]
    function = bad_attendance_rate if sys.argv[1] == 'bad' else attendance_rate
    actual = function(statuses)
    print('actual:', actual, 'expected:', 66.67, flush=True)
    assert actual == 66.67, 'Counterexample: numerator and denominator follow the wrong rule'
    print('verified fixture')


if __name__ == '__main__':
    main()
