import Link from 'next/link'
import { ChevronRight, Clock3, FileText, PencilLine } from 'lucide-react'

type DraftCard = { href: string; title: string | null; pending: boolean }

export function TeacherExamDraftPanel({
    cards,
    status,
}: {
    cards: DraftCard[]
    status: 'loading' | 'failed' | 'ready'
}) {
    return (
        <aside className="room-draft-panel" aria-labelledby="draft-list-title">
            <header className="room-draft-heading">
                <span className="room-draft-icon"><Clock3 size={20} aria-hidden="true" /></span>
                <h2 id="draft-list-title">Kỳ thi nháp</h2>
                {cards.length > 0 && <span className="room-draft-count" aria-label={`${cards.length} kỳ thi nháp`}>{cards.length}</span>}
            </header>
            <p className="room-draft-description">Các kỳ thi đang soạn thảo, chưa hoàn tất.</p>
            {status === 'loading' && <p className="room-draft-message" role="status">Đang tải bản nháp…</p>}
            {status === 'failed' && <p className="room-draft-message" role="status">Chưa tải được bản nháp từ hệ thống.</p>}
            {status === 'ready' && cards.length === 0 && (
                <p className="room-draft-message room-draft-empty">Chưa có kỳ thi nháp.</p>
            )}
            {cards.length > 0 && (
                <ul className="room-draft-list" aria-labelledby="draft-list-title" tabIndex={cards.length > 4 ? 0 : undefined}>
                    {cards.map(card => (
                        <li key={card.href}>
                            <Link className="room-draft-link" href={card.href}>
                                <span className="room-draft-file"><FileText size={20} aria-hidden="true" /></span>
                                <span className="room-draft-copy">
                                    <strong>{card.title?.trim() || 'Kỳ thi chưa có tên'}</strong>
                                    <small data-pending={card.pending || undefined}>
                                        <PencilLine size={13} aria-hidden="true" />
                                        {card.pending ? 'Chưa đồng bộ' : 'Đang chỉnh sửa'}
                                    </small>
                                </span>
                                <ChevronRight size={17} aria-hidden="true" />
                            </Link>
                        </li>
                    ))}
                </ul>
            )}
        </aside>
    )
}
