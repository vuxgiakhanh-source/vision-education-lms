"""G6 transfer answer: fixed-clock library renewal, no HTTP or persistence."""
from dataclasses import dataclass, replace
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Loan:
    id: int
    borrower_id: int
    due_at: datetime
    renewals: int = 0
    returned: bool = False


def renew_loan(loan, actor_id, other_reader_waiting, now):
    # The HTTP boundary must resolve actor and the queue from trusted server data.
    if loan.due_at.tzinfo is None or now.tzinfo is None:
        raise ValueError('Use timezone-aware datetimes')
    if actor_id != loan.borrower_id:
        raise PermissionError('Only the borrower may request renewal')
    if loan.returned:
        raise ValueError('Loan already returned')
    if now >= loan.due_at:
        raise ValueError('Loan reached its due time')
    if loan.renewals >= 2:
        raise ValueError('Renewal limit reached')
    if other_reader_waiting:
        raise ValueError('Another reader is waiting')
    return replace(loan, due_at=loan.due_at + timedelta(days=7),
                   renewals=loan.renewals + 1)
